import sys
import argparse
import whois # pip3 install python-whois
from whois import whois

class color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def run(args):
    #domains = []
    for word in args.words:
        # clean the line
        word = word.replace('\n','').replace('\r','').replace(' ','')
        if len(word) > 0:
            for tld in ['.com','.io']:
                domain = word+tld
                try:
                    result = whois( domain )
                    print( "["+color.FAIL+"Taken"+color.ENDC+"]\t", domain )
                except whois.parser.PywhoisError:
                    print( "["+color.OKGREEN+"Available"+color.ENDC+"]\t", domain )

def main(argv):
    parser = argparse.ArgumentParser(description='Find available domains')
    parser.add_argument('words', type=argparse.FileType('r'), help='words')

    if len(argv) == 0:
        parser.print_help()
        sys.exit(0)
    try:
        args = parser.parse_args() 
        run( args )
    except IOError as err: 
        print(str(type(err)) + " : " + str(err))
        parser.print_help()
        sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])