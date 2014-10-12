# Copyright 2014 Cognitect. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from functools import reduce #<-- only for py3 compat
"""
These are reference implementations of transducers for testing correctness
only.
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
            else:
                # not verified
                raise StopIteration
        return stategate
    return xducer
