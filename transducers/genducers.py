# Build this to reduce over the final generator, compose to get generator.
from functools import partial

def compose(*fns):
    """Inverted from transducers due to generator semantics."""
    return reduce(lambda f,g: lambda x: g(f(x)), fns)

def append(l, item):
    l.append(item)
    return l

def mapgen(f):
    """Only perserved as artifact of exploration thus far. This is slower than
    a partial native map call."""
    def generator(coll):
        for item in coll:
            yield f(item)
    return generator

def filtergen(f):
    """Only perserved as artifact of exploration thus far. This is slower than
    a partial native filter call."""
    def generator(coll):
        for item in coll:
            if f(item):
                yield item
    return generator


def taking(n):
    """Taking transducer."""
    def generator(coll):
        for i, item in enumerate(coll):
            if i >= n:
                raise StopIteration
            yield item
    return generator


def cat(coll):
    for item in coll:
        for subitem in item:
            yield subitem


def mapping(f):
    return partial(map, f)


def filtering(f):
    return partial(filter, f)

def dedupe(coll):
    prev = next(coll)
    yield prev
    for item in coll:
        if item != prev:
            prev = item
            yield item

def mapcatting(f):
    return compose(mapping(f), cat)


def genduce(generator, reducer, start, coll):
    return reduce(reducer, generator((a for a in coll)), start)

## -- for reference, naive transducer transliteration
## -- is a constant factor of ~5x slower.

# Fastest, about 2-2.5 x inline generator speed.
def perf_genduced(reducer=append, init=[]):
    """Parameters let me test other reducing/init value."""
    return genduce(compose(mapping(msq), filtering(fodd)),
                     reducer,
                     init,
                     range(100000))

# Slower, about 4 x inline generator speed
def perf_custom_genduced(reducer=append, init=[]):
    return genduce(compose(mapgen(msq), filtergen(fodd)),
            reducer,
            init,
            range(100000))

def test_mapcatting():
    return genduce(mapcatting(reversed), append, [],
                   [range(10), range(10), range(10)])


# -- check equivalence --
# functions
fodd = lambda x: x%2
msq = lambda x: x*x

## Using genducers -- twice as fast as naive transducers
def big_comp():
    return genduce(compose(mapcatting(reversed),
                             mapping(msq),
                             filtering(fodd),
                             taking(6)),
                     append, [], [range(10000), range(10000), range(10000)])

def test_dedupe():
    return genduce(dedupe, append, [], [1, 1, 2, 3, 4, 4, 4, 5, 1])
