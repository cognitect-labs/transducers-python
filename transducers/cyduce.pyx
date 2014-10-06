"""
Experimenting with Cython performance options for particular reducing functions
and or transducer function inputs that might be perf bottlenecks.
"""

def compose(*fns):
    return reduce(lambda f,g: lambda x: f(g(x)), fns)

def append(l, val):
    l.append(val)
    return l

def mapping(f):
    return lambda step: lambda r, x: step(r, f(x))

def filtering(pred):
    """Transducer version of filtering."""
    return lambda step: lambda r, x: step(r, x) if pred(x) else r

def fodd(int x):
    return x % 2

def msq(int x):
    return x * x

def transduce(transducer, reducer, start, coll):
    return reduce(transducer(reducer), coll, start)

# This benchmarks at 1.5x speed of inline generator solution, but
# requires all code to be written in Cython. Basically we lose some
# of the function call overhead due to C loop optimization and typing
# fodd and msq.
def perf_transduced():
    """Parameters let me test other reducing/init value."""
    return transduce(compose(mapping(msq), filtering(fodd)),
                     append,
                     [],
                     range(100000))
