import argparse
import sys
import json
import requests
import base64
import time
from git import Repo
import tempfile
import shutil
import os
import stat
import glob
import re
import xml.etree.ElementTree as ET

SLEEP = .3

def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

def parse_file(filename, relative_filename, full_filename):
    should_check = False
    try:
        with open(full_filename,'r') as stream:
            content = stream.read()
            if "--no-sandbox" in content:
                return True
    except UnicodeDecodeError as e:
        pass


def parse_clone_mode( args ):
    for target in args.targets:
        repo_resp = requests.get("https://api.github.com/users/{}/repos?per_page=1000".format(target)).json()

        for repo_json in repo_resp:
            git_url = repo_json['html_url']

            print( git_url )

            project_path = tempfile.mkdtemp()
            Repo.clone_from(git_url, project_path, depth=1)
            repo = Repo(project_path)

            found=False
            for root, subdirs, files in os.walk(project_path):
                if found:
                    break

                for filename in files:
                    full_filename = os.path.join(root, filename)
                    relative_filename = full_filename[len(project_path)+1:]
                    try:
                        found = parse_file( filename, relative_filename, full_filename )
                        if found:
                            print( "-", relative_filename )

                    except:
                        print("Error: parsing", relative_filename, "\n", sys.exc_info()[0])

                    if found:
                        break
                shutil.rmtree(project_path, onerror=del_rw)



def main(argv):
    parser = argparse.ArgumentParser(description='Find target golang projects for orgs.')
    parser.add_argument('--verbose', '-v', default=False, action="store_true", help="verbose mode")
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
