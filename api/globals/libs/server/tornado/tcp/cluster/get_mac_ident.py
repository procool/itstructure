import time
import random
import hashlib
 
#  mac + time + pid + rand
 
def get_new_ident(pid=None):
    ''' Build a new Ident '''

    pid = pid is not None and str(pid) or ''
 
    ### Time:
    t1 = time.time()
 
    ### Random:
    lst = ['A', 'B', 'C', 1, 2, 3]
    random.shuffle(lst)
    rnd =  ''.join(map(str, lst))
 
    ### Mac:
    import uuid
    hdr="\xff"*6
    mac=uuid.getnode()
    mactxt="%012X"%mac
    ###print mactxt
 
    ##base = hashlib.md5(str(t1)).hexdigest()
    ##base = hashlib.md5(str(t1)+rnd).hexdigest()
    base = hashlib.md5(str(t1)+rnd+mactxt+pid).hexdigest()
    return ''.join((base))
 
if __name__ == '__main__':
    print get_new_ident(34578)

