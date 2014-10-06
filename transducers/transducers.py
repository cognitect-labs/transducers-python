from functools import reduce #<-- only for py3 compat

"""
Transducers test implementation in Python. It works, but concern is that it's
about 4x slower than most cases (changed n, but not complexity of process).
Assumption is that you'd see gains with non-trivial collection/building, etc.
however as transducers apply transform in reduce process instead of to finished
collection, as builtin Python routines do (except in non-trivial applications
of comprehensions/generators, splat tricks, etc.)

Some perf tests are provided. A full set of transducers as per spec is not
yet included.

** Generalization power advantage still holds for transducers, all performance
concerns aside.
"""
def compose(*fns):
    """Compose functions using reduce on splat.

    compose(f, g) reads 'f composed with g', or f(g(x))
    """

    return reduce(lambda f,g: lambda x: f(g(x)), fns)

def transduce(transducer, reducer, start, coll):
    """Return the results of calling transduce on the reducing function,
    can compose transducers using compose defined above.

    Note: could possibly switch coll/start order if we want to match Python
    reduce instead of Clojure reduce.
    """
    return reduce(transducer(reducer), coll, start)

def mapping(f):
    """Transducer version of map."""
    return lambda step: lambda r, x: step(r, f(x))

def filtering(pred):
    """Transducer version of filtering."""
    return lambda step: lambda r, x: step(r, x) if pred(x) else r

def cat(step):
    """Cat helper function/transducer."""
    return lambda r, x: reduce(step, x, r)

def mapcatting(f):
    """Mapcat transducer."""
    return compose(mapping(f), cat)

def taking(n):
    """Taking transducer."""
    def xducer(step):
        outer_vars = {"counter": 0} # <-- ugh, state in closures w/o
                                    #     nonlocal from Python 3 :(
        def stategate(x, r):
            if outer_vars["counter"] < n:
                outer_vars["counter"] += 1
                return step(x, r)
            return x
        return stategate
    return xducer

def taking_while(pred):
    """TODO"""
    pass
