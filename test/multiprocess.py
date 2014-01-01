import promises.multiprocess as pmp
from time import sleep

from functools import partial

def work(i):
    sleep(1)
    print "Hello World: Worker ID %i" % i
    sleep(5)
    return i


def broke(i):
    sleep(1)
    print "Wello Horld: Broken Worker ID %i" % i
    sleep(5)
    raise Exception("tummy ache")


with pmp.ProxyPromising() as p:
    val_broken = p.promise(partial(broke, 10))

    val2 = p.promise(partial(work, 2))
    val3 = p.promise(partial(work, 3))
    val4 = p.promise(partial(work, 4))
    val5 = p.promise(partial(work, 5))
    val6 = p.promise(partial(work, 6))
    val7 = p.promise(partial(work, 7))


print "val7 is", val7
print "val6 is", val6
print "val5 is", val5
print "val4 is", val4
print "val3 is", val3
print "val2 is", val2

print "val_broken is", val_broken

