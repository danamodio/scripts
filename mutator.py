import random
import urllib.parse

words = []
with open('/usr/share/dict/words','r') as f:
    words = f.read().splitlines()

"""
ENCODERS
"""
def capitalize(payload):
    return payload.capitalize()

def all_upper(payload):
    return payload.upper()

def all_lower(payload):
    return payload.lower()

def all_random_case(payload):
    barr = bytearray( payload )
    for i in range(0, len(barr)):
        if barr[i] < 123 and barr[i] > 64:
            try:
                barr[i] = ord( random.choice([all_upper, all_lower])( chr(barr[i]) ) )
            except TypeError as e:
                pass
    return bytes( barr )

def encode_url(payload):
    return urllib.parse.quote_plus( payload ).encode()

"""
LISTS
"""
def get_word():
    word = random.choice( words ).encode()
    word = random.choice( [nop, capitalize, all_upper, all_lower, all_random_case] )( word )
    return word

"""
FUNCTIONS
"""
def insert(payload):
    barr = bytearray( payload )
    pos = random.randint(0, len(barr))
    char = random.randint(0, 255)
    barr.insert(pos, char)
    return bytes( barr )

def insert_word(payload):
    barr = bytearray( payload )
    pos = random.randint(0, len(barr))
    word = get_word()
    barr[pos:pos] = word
    return bytes( barr )

def swap(payload):
    barr = bytearray( payload )
    a = random.randint(0, len(barr)-1)
    b = random.randint(0, len(barr)-1)
    barr[a], barr[b] = barr[b], barr[a]
    return bytes( barr )

def delete(payload):
    barr = bytearray( payload )
    pos = random.randint(0, len(barr)-1)
    del( barr[pos] )
    return bytes( barr )

def replace(payload):
    barr = bytearray( payload )
    pos = random.randint(0, len(barr)-1)
    char = random.randint(0, 255)
    barr[pos] = char
    return bytes( barr )


def nop(payload):
    return payload


mutators = [nop, insert, insert_word, swap, delete, replace, capitalize, all_upper, all_lower, all_random_case, encode_url]
null_safe_mutators = [insert, insert_word, nop]


def get_samples(payload, num=10):
    res = []
    for i in range(0, num):
        if len(payload) == 0:
            res.append( random.choice(null_safe_mutators)(payload) )
        else:
            res.append( random.choice(mutators)(payload) )
    return res

def mutate(payload):
    return get_samples(payload)[0]
