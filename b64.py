import mutator
import base64
import binascii


baseline = base64.b64encode(b'test')

children = mutator.get_samples( baseline, num=10)

running = True
while(running):
    for c in range(0, len(children)):
        #print(c, children[c])
        try:
            decoded = base64.b64decode( children[c] )
            if decoded:
                pass
                #print(c, children[c], decoded)
            else:
                if random.randint(0,10) == 7:
                    # back to basics .. no instrumentation so ..
                    children[c] = mutator.mutate( baseline )
                else:
                    children[c] = mutator.mutate( children[c] )
            #running = False
        except binascii.Error as  e:
            pass
            #print( c, type(e), children[c] )
