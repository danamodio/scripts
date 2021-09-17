import requests
import xmlrpc.client
import argparse
import re


RULES = [
    'Authorization: [\w\d\+/=]+',
    'AKIA[0-9A-Z]{16}', # Amazon AWS Access Key ID
    '-----BEGIN RSA PRIVATE KEY-----', # RSA private key
    'https://[\w.]+box.com[/?=&\w\d]+', # box share links
    'https:\/\/docs\.google\.com[/?=&\-#\w\d]+', # google docs links
    "[a-zA-Z]{3,10}://[^/\\s:@]{3,20}:[^/\\s:@]{3,20}@.{1,100}[\"'\\s]", # password in URL
    #"[pP]assword(\s)?(:)?(\s)+[\41-\176]+" # inline password
    "[pP]assword[\s:]+[\41-\176]+", # inline password
]


def check_secrets( content ):
    matches = []
    for rule in RULES:
        matches.extend( re.findall(rule, content) )
    return matches

def get_page( args, page_id ):
    resp = requests.get( "{}/rest/api/content/{}?expand=body.storage".format(args.target, page_id), auth=( args.username, args.password ) ).json()
    print( "[{}]".format(page_id), resp['title'], ":", "{}{}".format(args.target, resp['_links']['webui']) )

    content = resp['body']['storage']['value']
    matches = check_secrets( content )
    if matches:
        for match in matches:
            print( "-->", match )

def get_pages( args, uri='/rest/api/content/' ):
    resp = requests.get( args.target+uri, auth=( args.username, args.password ) ).json()

    for page in resp['results']:
        get_page( args, page['id'] )

    if 'next' in resp['_links']:
        get_pages( args, resp['_links']['next'] )


def main():
    parser = argparse.ArgumentParser(description="Confluence wiki scraper")
    parser.add_argument("-t", "--target", help="Wiki URL (only FQDN, no / and such)", required=True)
    parser.add_argument("-u", "--username", help="Login Username", required=True)
    parser.add_argument("-p", "--password", help="Login Password", required=True)
    parser.add_argument("-v", "--verbose", help="Enable debug logging", action="store_true")

    args = parser.parse_args()

    get_pages( args )

if __name__ == '__main__':
    main()
