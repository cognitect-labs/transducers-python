"""
Performance benchmarks not hooked to  anything yet (I've been using
%timeit in ipython).

:TODO: ------------------------- :TODO:
  Implement tests to:
[ ] benchmark implementations.
[ ] test equivalence of genducer and transducer implementations.
[ ] Do so through unit test class wrapper that takes functions and
    tests their behavior from both backends.
"""
##====================================
## Routines to test simple case here:
##====================================
# temporary wildcard import 
from transducers.genducers import *
from transducers.genducers import genduce as transduce
from transducers import genducers as G
from transducers import genducers as CG
from collections import deque
from functools import partial
from fractions import Fraction
from operator import add


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
    return transduce(compose(mapcatting(reversed),
                             mapping(msq),
                             filtering(fodd),
                             taking(6)),
                     append, [], [range(10000), range(10000), range(10000)])


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

def geometric_series(a, r):
    power = 0
    yield a
    while True:
        power += 1
        yield a * r**power

def test_generator_function_input(n):
    return G.genduce(G.taking(n),
                   add,
                   Fraction(0, 1),
                   geometric_series(Fraction(1, 1), Fraction(1, 2)))

# --- won't finish in current naive implementation ---
#
#           transduce(taking(n),
#                     add,
#                     Fraction(0, 1),
#                     geometric_series(Fraction(1, 1), Fraction(1, 2))))
#

def perf_genduced(reducer=append, init=[]):
    """Parameters let me test other reducing/init value."""
    return G.genduce(G.compose(G.mapping(msq), G.filtering(fodd)),
                     reducer,
                     init,
                     range(100000))

def test_mapcatting():
    return G.genduce(G.mapcatting(reversed), append, [],
                   [range(10), range(10), range(10)])

def Gbig_comp():
    return G.genduce(G.compose(G.mapcatting(reversed),
                             G.mapping(msq),
                             G.filtering(fodd),
                             G.taking(6)),
                     append, [], [range(10000), range(10000), range(10000)])

def test_dedupe():
    return G.genduce(G.dedupe, append, [], [1, 1, 2, 3, 4, 4, 4, 5, 1])

def Gtest_string():
    return G.genduce(G.compose(G.mapping(lambda x: x+x), G.taking(10000)),
                     add, "", "This is just some string!" * 5000)

def Ttest_string():
    return transduce(compose(mapping(lambda x:x+x), taking(10000)),
                     add, "", "This is just some string!" * 5000)

def CGtest_string():
    return CG.genduce(CG.compose(CG.mapping(lambda x:x+x), CG.taking(10000)),
                     add, "", "This is just some string!" * 5000)

def Gtothefront():
    return G.genduce(G.compose(G.taking(5), G.mapping(msq)),
                     dleft_append, deque(), range(10000))

def Gpartition_all_mapping():
    return G.genduce(G.compose(G.partition_all(4), G.mapping(list)), append, [], range(10))

if __name__=="__main__":
    """For now, just verify no errors on running."""
    perf_transduced()
    perf_transduced_deque()
    tothefront()
    perf_mapcatting()
    perf_taking()
    big_comp()
    test_dedupe()
    Gtest_string()
    CGtest_string()
    Ttest_string()
    Gbig_comp()
    perf_genduced()
    test_mapcatting()
    Gpartition_all_mapping()
