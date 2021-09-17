import argparse
import sys
import json
import requests
import base64
import yaml
import time
from yaml.constructor import SafeConstructor
from git import Repo
import tempfile
import shutil
import os
import stat
import glob
import re

SLEEP = .5

def add_bool(self, node):
    return self.construct_scalar(node)

SafeConstructor.add_constructor(u'tag:yaml.org,2002:bool', add_bool)

def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

def parse_clone_mode( args ):
    for target in args.targets:
        repo_resp = requests.get("https://api.github.com/users/{}/repos?per_page=1000".format(target)).json()

        for repo_json in repo_resp:
            git_url = repo_json['html_url']
            print( git_url )

            project_path = tempfile.mkdtemp()
            Repo.clone_from(git_url, project_path)
            repo = Repo(project_path)

            for root, subdirs, files in os.walk(project_path):
                for filename in files:
                    full_filename = os.path.join(root, filename)
                    relative_filename = full_filename[len(project_path)+1:]
                    if relative_filename.startswith('.github/workflows'):
                        if relative_filename.endswith('.yml'):
                            with open(full_filename,'r') as stream:
                                content = stream.read()
                                parsed =  yaml.safe_load( content )
                                if 'on' in parsed and 'pull_request' in parsed['on']:
                                    print("*", relative_filename )
                                    secrets =  set()
                                    for match in re.findall( "\$\{\{\s*secrets\.[a-zA-Z0-9_]+\s*\}\}", content ):
                                        secrets.add( match.replace("{","").replace("}","").replace(" ","").replace("$","").split(".")[1] )
                                    if len(secrets) > 0:
                                        print("Secrets:")
                                        for secret in secrets:
                                            print("-", secret)

                                    env_vars =  set()
                                    for match in re.findall( "\$\{\{\s*env\.[a-zA-Z0-9_]+\s*\}\}", content ):
                                        env_vars.add( match.replace("{","").replace("}","").replace(" ","").replace("$","").split(".")[1] )
                                    if len(env_vars) > 0:
                                        print("Env Vars:")
                                        for env_var in env_vars:
                                            print("-", env_var)

                                    if "actions/cache" in content:
                                        print("actions/cache:")
                                        for job in parsed['jobs']:
                                            for step in parsed['jobs'][job]['steps']:
                                                if 'uses' in step:
                                                    if 'actions/cache' in step['uses']:
                                                        if 'with' in step:
                                                            if 'path' in step['with']:
                                                                print( "-", step['with']['path'])
                                    for job in parsed['jobs']:
                                        for step in parsed['jobs'][job]['steps']:
                                            if 'runs-on' in step and 'self-hosted' in step['runs-on']:
                                                print("Self-hosted runner!")

            shutil.rmtree(project_path, onerror=del_rw)

def main(argv):
    parser = argparse.ArgumentParser(description='Find github vulnerable workflow actions for org.')
    parser.add_argument('targets', nargs='+', help='target orgs')

    if len(argv) == 0:
        parser.print_help()
        sys.exit(0)
    try:
        global args
        args = parser.parse_args()
        parse_clone_mode( args )
    except IOError as err:
        print(str(type(err)) + " : " + str(err))
        parser.print_help()
        sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])
