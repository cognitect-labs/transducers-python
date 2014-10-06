"""
Performance benchmarks not hooked to  anything yet (I've been using
%timeit in ipython).
"""
##====================================
## Routines to test simple case here:
##====================================
# temporary wildcard import 
from transducers.transducers import *
from collections import deque
from functools import partial

# Reducing functions
def dright_append(d, item):
    d.append(item)
    return d

def dleft_append(d, item):
    d.appendleft(item)
    return d

def append(l, item):
    """Append for reduce - this append benchmarked fastest thus far.

    Beats:
    Addition operator, splat tricks, checking anything.
    """
    l.append(item)
    return l

# functions
fodd = lambda x: x%2
msq = lambda x: x*x

## Using transducers
def big_comp():
    return transduce(compose(mapcatting(lambda x:
                                          [a for a in reversed(x)]),
                             mapping(msq),
                             filtering(fodd),
                             taking(6)),
                     append, [], [range(20), range(50)])


def perf_transduced(reducer=append, init=[]):
    """Parameters let me test other reducing/init value."""
    return transduce(compose(mapping(msq), filtering(fodd)),
                     reducer,
                     init,
                     range(100000))

def perf_transduced_deque():
    """Perf transduced with deque instead of list."""
    return perf_transduced(dright_append, init=deque())

def perf_mapcatting():
    return transduce(mapcatting(lambda x: [a for a in reversed(x)]),
                     append, [], [[4,3,2], [7,6,5]])

def perf_taking():
    return transduce(taking(5), append, [], (1, 2, 3, 4, 5, 6, 7, 8, 9, 10))

def tothefront():
    return transduce(compose(taking(5), mapping(msq)),
                     dleft_append, deque(), range(10000))

##### Performance comparisons ######
# these are not transducers, just Python alternatives we need to compare
# performance to.

## Naive map-filter using Python builtins.
def perf_mf():
    return map(msq,
           filter(fodd, 
           range(100000)))

## Map filter reduce using compose with Python builtins.
def perf_composed():
    return compose(partial(map, msq),
                   partial(filter, fodd))(range(100000))

## Fulfilling conditions in imperatively defined generator.
def perf_gen():
    def inner():
        for a in range(100000):
            if a % 2:
                yield a**2
    return list(inner())

## This is checking the influence of just append.
def perf_gen_append():
    coll = {"l": []}
    def inner():
        for a in range(100000):
            if a % 2:
                yield coll["l"].append(a**2)
    return [a for a in inner()][-1]

## Python list comprehension version (typical Pythonic solution)
def perf_comprehension():
    return [a**2 for a in range(100000) if a % 2]

if __name__=="__main__":
    """For now, just verify no errors on running."""
    perf_transduced()
    perf_transduced_deque()
    tothefront()
    perf_mapcatting()
    perf_taking()
    big_comp()
