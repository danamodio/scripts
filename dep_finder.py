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

npm_cache = {}
def check_npm( pack ):
    #print(pack, type(pack))
    if not pack in npm_cache:
        time.sleep( SLEEP )
        npm_resp = requests.get("https://registry.npmjs.org/{}".format(pack))#.json()
        if npm_resp.status_code == 200:
            npm_cache[pack] = True
        elif npm_resp.status_code == 404:
            npm_cache[pack] = False
        else:
            print("ERROR:", npm_resp.status_code, npm_resp.text)
            return None
    return npm_cache[pack]


def check_npm_deps( pack ):
    # https://docs.npmjs.com/cli/v6/configuring-npm/package-json
    pack_contexts = ['dependencies', 'devDependencies', 'peerDependencies', 'bundledDependencies', 'optionalDependencies']
    for context in pack_contexts:
        if context in pack:
            #for dep in [x.decode() for x in pack[context].keys()]:
            for dep in pack[context].keys():
                in_npm = check_npm( dep )
                print("   -", context, dep, pack[context][dep], in_npm)

pypi_cache = {}
def check_pypi( dep ):
    if not dep in pypi_cache:
        time.sleep( SLEEP )
        pypi_resp = requests.get("https://pypi.org/simple/{}/".format(dep))#.json()
        if pypi_resp.status_code == 200:
            pypi_cache[dep] = True
        elif pypi_resp.status_code == 404:
            pypi_cache[dep] = False
        else:
            print("ERROR:", pypi_resp.status_code, pypi_resp.text)
            return None
    return pypi_cache[dep]

def check_pypi_deps( deps ):
    for dep in deps:
        #    if not line.startswith("#"):
        dep_n = dep
        dep_v = ""
        if ";" in dep_n:
            dep_n = dep_n.split(';')[0].strip()

        if "[" in dep_n:
            dep_n = dep_n.split('[')[0].strip()

        if "==" in dep_n:
            dep_n = dep_n.split("==")[0].strip()
        elif ">=" in dep_n:
            dep_n = dep_n.split('>=')[0].strip()
        elif "<=" in dep_n:
            dep_n = dep_n.split('<=')[0].strip()
        elif "~=" in dep_n:
            dep_n = dep_n.split('~=')[0].strip()
        elif "=" in dep_n:
            dep_n = dep_n.split('=')[0].strip()
        elif "<" in dep_n:
            dep_n = dep_n.split('<')[0].strip()
        elif ">" in dep_n:
            dep_n = dep_n.split('>')[0].strip()
        else:
            dep_n = dep_n
        in_pypi = check_pypi( dep_n )
        print( "   -", dep, in_pypi )

gems_cache = {}
def check_gem( dep ):
    if not dep in gems_cache:
        time.sleep( SLEEP )
        #print( "https://rubygems.org/api/v1/gems/{}.json".format(dep) )
        gem_resp = requests.get("https://rubygems.org/api/v1/gems/{}.json".format(dep))

        if gem_resp.status_code  == 200:
            gems_cache[dep] = True
        elif gem_resp.status_code  == 404:
            gems_cache[dep] = False
        else:
            print("ERROR:", gem_resp.status_code, gem_resp.text)
            return None
    return gems_cache[dep]

def check_ruby_deps( deps ):
    for dep in deps:
        dep_n = ""
        if "(" in dep:
            dep_n = dep.split("(")[1].split()[0]
        else:
            dep_n = dep.split()[1]
        dep_n = dep_n.replace(",","").replace("'","").replace('"','').replace("<","").replace("~","").replace("=","").replace(">","").replace(")","").replace("(","")

        in_gems = check_gem( dep_n )
        print("   -", dep, in_gems)

nuget_cache = {}
def check_nuget( dep ):
    if not dep in nuget_cache:
        time.sleep( SLEEP )
        nuget_resp = requests.get("https://www.nuget.org/api/v2/package/{}/".format(dep))

        if nuget_resp.status_code  == 200:
            nuget_cache[dep] = True
        elif nuget_resp.status_code  == 404:
            nuget_cache[dep] = False
        else:
            print("ERROR:", nuget_resp.status_code, nuget_resp.text)
            return None
    return nuget_cache[dep]

def check_nuget_deps( deps ):
    for dep in deps:
        in_nuget = check_nuget( dep )
        print("   -", dep, in_nuget)

def parse_file(filename, relative_filename, full_filename):
    if filename == "package.json":
        print( "-", relative_filename )
        with open(full_filename,'r') as stream:
                content = stream.read()
                parsed = json.loads( content )
                #print( json.dumps( parsed ) )
                check_npm_deps( parsed )
    elif filename == "package-lock.json":
        print( "-", relative_filename )
    elif filename.endswith('.gemspec'):
        print("-", relative_filename)
        with open(full_filename,'r') as content:
            deps = [x.strip() for x in content.readlines()]
            deps = [x for x in deps if "_dependency" in x and not x.startswith("#")]
            check_ruby_deps( deps )
    elif filename == 'Gemfile':
        print('-', relative_filename)
        with open(full_filename,'r') as content:
            deps = [x.strip() for x in content.readlines()]
            deps = [x for x in deps if x.startswith("gem ")]
            check_ruby_deps( deps )
    elif filename == 'Gemfile.lock':
        print('-', relative_filename)
    elif filename.endswith('requirements.txt'):
        print( '-', relative_filename)
        with open(full_filename,'r') as content:
            deps = [x.strip() for x in content.readlines()]
            deps = [x for x in deps if not x.startswith("#") and x != "" and not x.startswith("-")]
            check_pypi_deps( deps )
    elif filename.lower() == "setup.py":
        print( '-', relative_filename)
    elif filename == "packages.config":
        print( '-', relative_filename)
    elif filename == "nuget.config":
        print( '-', relative_filename)
    elif filename == "NuGet.Config":
        print( '-', relative_filename)
    elif filename.lower().endswith('.csproj'):
        print( '-', relative_filename)
        tree = ET.parse( full_filename )
        root = tree.getroot()
        deps = [x.get('Include') for x in root.findall('ItemGroup/PackageReference')]
        check_nuget_deps( deps )

def parse_clone_mode( args ):
    for target in args.github:
        repo_resp = requests.get("https://api.github.com/users/{}/repos?per_page=1000".format(target)).json()

        for repo_json in repo_resp:
            git_url = repo_json['html_url']
            print( git_url )

            project_path = tempfile.mkdtemp()
            Repo.clone_from(git_url, project_path, depth=1)
            repo = Repo(project_path)

            for root, subdirs, files in os.walk(project_path):
                for filename in files:
                    full_filename = os.path.join(root, filename)
                    relative_filename = full_filename[len(project_path)+1:]
                    try:
                        parse_file( filename, relative_filename, full_filename )
                    except:
                        print("Error: parsing", relative_filename, "\n", sys.exc_info()[0])

            # clean up
            shutil.rmtree(project_path, onerror=del_rw)

def run_target( args ):
    for target in args.dir:
        for root, subdirs, files in os.walk( target ):
            for filename in files:
                full_filename = os.path.join(root, filename)
                relative_filename = full_filename[len( target )+1:]

                parse_file( filename, relative_filename, full_filename )


def run_tests():
    for root, subdirs, files in os.walk("./data"):
        for filename in files:
            full_filename = os.path.join(root, filename)
            relative_filename = full_filename[len("./data")+1:]

            parse_file( filename, relative_filename, full_filename )

def main(argv):
    parser = argparse.ArgumentParser(description='Find github vulnerable workflow actions for org.')
    parser.add_argument('--github', nargs='+', help='github target orgs', required=False)
    parser.add_argument('--test', default=False, action="store_true", help="Run tests")
    parser.add_argument('--repo', '-r', required=False, choices=['npm','pypi','gems','nuget'], help='read list from stdiin and search target repo')
    parser.add_argument('--dir', '-d', nargs='+', help='target directories')#, required=False)
    parser.add_argument('--verbose', '-v', default=False, action="store_true", help="verbose mode")

    if len(argv) == 0:
        parser.print_help()
        sys.exit(0)
    try:
        global args
        args = parser.parse_args()
        if args.test:
            run_tests()
        elif args.github:
            parse_clone_mode( args )
        elif args.repo:
            for line in sys.stdin:
                dep = line.strip()
                found = None
                if args.repo == 'npm':
                    found = check_npm( dep )
                elif args.repo == 'pypi':
                    found = check_pypi( dep )
                elif args.repo == 'gems':
                    found = check_gem( dep )
                elif args.repo == 'nuget':
                    found = check_nuget( dep )
                if found and args.verbose:
                    print(dep, found)
                else:
                    print(dep, found)
        elif args.dir:
            run_target( args )

    except IOError as err:
        print(str(type(err)) + " : " + str(err))
        parser.print_help()
        sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])
