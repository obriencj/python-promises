import promises.multiprocess as pmp
from time import sleep

from functools import partial

def work(i):
    sleep(1)
    print "Hello World: Worker ID %i" % i
    sleep(5)
    print "Done with work: %i" % i
    return i


def broke(i):
    sleep(1)
    print "Wello Horld: Broken Worker ID %i" % i
    sleep(5)
    print "herp derp: %i" % i
    raise Exception("tummy ache")


with pmp.ProxyPromising() as p:
    val_broken = p.promise(partial(broke, 10))
    print "promised val_broken"

    val2 = p.promise(partial(work, 2))
    print "promised val2"
    
    val3 = p.promise(partial(work, 3))
    print "promised val3"

    val4 = p.promise(partial(work, 4))
    print "promised val4"

    val5 = p.promise(partial(work, 5))
    print "promised val5"

    val6 = p.promise(partial(work, 6))
    print "promised val6"

    val7 = p.promise(partial(work, 7))
    print "promised val7"

print "left managed scope"


print "val2 is", val2
print "val3 is", val3
print "val4 is", val4
print "val5 is", val5
print "val6 is", val6
print "val7 is", val7

try:
    print "val_broken is", val_broken
except Exception, e:
    print e

try:
    print "val_broken is", val_broken
except Exception, e:
    print e

