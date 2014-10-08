# Build this to reduce over the final generator, compose to get generator.
from functools import partial

def compose(*fns):
    """Inverted from transducers due to generator semantics."""
    return reduce(lambda f,g: lambda x: g(f(x)), fns)


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
    """Some functools can handle generator input correctly."""
    return partial(map, f)


def filtering(f):
    """Some functools can handle generator input correctly."""
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
