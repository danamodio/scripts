import sys
import argparse
import requests
import tarfile
import re
import logging
#try:
#    from BytesIO import BytesIO ## for Python 2
#except ImportError:
from io import BytesIO ## for Python 3


target_files = [
    ".aws/credentials",
    ".bash_history",
    ".sh_history",
    ".ssh/id_rsa",
    ".azure/accessTokens.json",
    ".docker/config.json",
    "entry_point.sh"
]

class DockerChecker:
    def __init__(self, args):
        logging.debug( args )
        self.arg_all_tags = True
        self.image = args.target.split(":")[0]
        if "/" in self.image:
            self.library = self.image.split("/")[0]
            self.image = self.image.split("/")[1]
        else:
            self.library = "library"
        self.tag= args.target.split(":")[1]

        print("Image:", self.image)
        print("Library:", self.library)
        print("Tag:", self.tag)

        self.registry_url=args.registry
        self.auth_url=args.auth
        self.svc_url=args.service

    def get_auth_token(self):
        resp = requests.get( f"{self.auth_url}/token?service={self.svc_url}&scope=repository:{self.library}/{self.image}:pull" ).json()
        return resp['token']

    def get_manifest(self, token):
        headers = {
            "Authorization": "Bearer {}".format(token),
            "Accept" : "application/vnd.docker.distribution.manifest.list.v2+json",
            "Accept" : "application/vnd.docker.distribution.manifest.v1+json",
            "Accept" : "application/vnd.docker.distribution.manifest.v2+json",
        }
        resp = requests.get( f"{self.registry_url}/v2/{self.library}/{self.image}/manifests/{self.tag}", headers=headers)
        logging.debug( resp.headers )
        resp_json = resp.json()
        logging.debug( resp_json)

        return resp_json

    def get_blob(self, token, digest):
        headers = {
            "Authorization": "Bearer {}".format(token),
        }
        resp = requests.get( f"{self.registry_url}/v2/{self.library}/{self.image}/blobs/{digest}", headers=headers)
        resp_tgz = tarfile.open( fileobj=BytesIO(resp.content) , mode="r:gz")
        for member in resp_tgz.getmembers():
            logging.debug( member.name )
            if 'entropy' in member.name.lower():
                print( "*", member.name )
            elif 'random' in member.name.lower():
                print( "*", member.name )
        resp_tgz.close()

    def run(self):
        token = self.get_auth_token()
        manifest = self.get_manifest( token )

        for layer in manifest['layers']:
            #logging.debug( layer )
            print( "Digest:", layer['digest'] )
            self.get_blob( token, layer['digest'] )
            #print( get_blob( token, layer['digest'] ))

def main(argv):
    parser = argparse.ArgumentParser(description='Check docker images for exposed secrets')
    parser.add_argument('-r', '--registry', default='https://registry-1.docker.io', help='Registry URL')
    parser.add_argument('-a', '--auth', default='https://auth.docker.io', help='Auth URL')
    parser.add_argument('-s', '--service', default='registry.docker.io', help='Service URL')
    parser.add_argument('-d', '--debug', default=False, action="store_true", help="Print debug data.")
    parser.add_argument('--tags', default=False, action="store_true", help="Pull all tags/versions.")
    parser.add_argument('target', help='Target image:tag, e.g. golang:latest')

    if len(argv) == 0:
        parser.print_help()
        sys.exit(0)
    try:
        args = parser.parse_args()

        if args.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        app = DockerChecker( args )
        app.run()
    except IOError as err:
        print(str(type(err)) + " : " + str(err))
        parser.print_help()
        sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])
