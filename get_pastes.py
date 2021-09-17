import requests
from html.parser import HTMLParser
import time
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:75.0) Gecko/20100101 Firefox/75.0',
}

class LinkParser(HTMLParser):
    def __init__(self):
        self.links = []
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag=="a":
            for attr in attrs:
                if attr[0] == 'href':
                    self.links.append( attr[1] )

class TextAreaParser(HTMLParser):
    def __init__(self):
        self.inTextarea = False
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag=="textarea":
            self.inTextarea = True

    def handle_endtag(self, tag):
        if tag=="textarea":
            self.inTextarea = False

    def handle_data(self, data):
        if self.inTextarea:
            print("*"*100)
            print(data)
            print("*"*100)

def get_paste_by_id(paste_id):
    r = requests.get('https://pastebin.com'+paste_id, headers=headers)
    tp = TextAreaParser()
    tp.feed( r.text )

def get_public_pastes():
    r = requests.get('https://pastebin.com/archive', headers=headers)
    #print( r.status_code )
    #print( r.text )
    lp = LinkParser()
    lp.feed( r.text )
    for link in lp.links:
        if len( link ) == 9:
            print("Paste: "+ link)
            get_paste_by_id( link )
            time.sleep( random.uniform(.5, 3) )

if __name__ == "__main__":
    get_public_pastes()
    #get_paste_by_id('/J')
