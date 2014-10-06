# Build this to reduce over the final generator, compose to get generator.
from functools import partial

# canned functions
fodd = lambda x: x%2
msq = lambda x: x*x

def compose(*fns):
    return reduce(lambda f,g: lambda x: f(g(x)), fns)

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
                q
                yield item
    return generator

def mapping(f):
    return partial(map, f)

def filtering(f):
    return partial(filter, f)

def genduce(generator, reducer, start, coll):
    return reduce(reducer, generator(coll), start)

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
