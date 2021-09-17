from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import JavascriptException
from selenium.common.exceptions import UnexpectedAlertPresentException

import json
import os
import subprocess

import hairball
import mutator

import time
import statistics
import random

import urllib.parse


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


def test(payload):
    prefix = "http://127.0.0.1:8001/xss?a="
    url = prefix + urllib.parse.quote_plus(payload)

    #print("-->", url)

    if url.startswith(prefix):
        try:
            driver.get( url )
            #print( httpResp )

            if "Forbidden" in driver.page_source:
                return False
            try:
                javaScript = "return xss"
                jsResult = driver.execute_script(javaScript)
                if jsResult == True:
                    #print("-->", url)
                    return True
            except JavascriptException as e:
                pass
        except UnexpectedAlertPresentException:
            return True
    return False

payloads = [
    #"<script>xss=true</script>",
    #"<img src=xss onerror=vuln(true)>",
    #"<body/onload=vuln(true)",
    #"<video src=1 onerror=vuln(true)>",
    #"<audio src=1 onerror=vuln(true)>"

    #"<iframe/onreadystatechange=vuln(true)>",
    #"<svg/onload=vuln(true)>"
]

with open("xss_payloads.txt", "r") as xss_payloads:
    for line in xss_payloads:
        payloads.append( line.rstrip() )

children = mutator.get_samples( random.choice( payloads ).encode() , num=10)

running = True
while(running):
    for c in range(0, len(children)):
        if test( children[c] ):
            if children[c] in wins:
                pass
            else:
                print("SUCESS", children[c])
                wins.append( children[c] )
        else:
            if random.randint(0,10) >= 5:
                if random.randint(0,10) >= 4 and len(wins) > 0:
                    fuzzed = subprocess.run(['radamsa', '-n', '1'], stdout=subprocess.PIPE, input=random.choice( wins ) ).stdout
                    children[c] = fuzzed
                else:
                    children[c] = random.choice( payloads ).encode()
            else:
                fuzzed = subprocess.run(['radamsa', '-n', '1'], stdout=subprocess.PIPE, input=children[c] ).stdout
                children[c] = fuzzed
