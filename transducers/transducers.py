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
import functools
from random import random
"""
These are reference implementations of transducers for testing correctness
only.
"""
class Reduced(object):
    """Only for 'is' comparison to signal early termination of reduce."""
    pass

def reduce(function, iterable, initializer=None):
    """Using Python documentation's function to allow capability to test for
    reduced state.
    """
    it = iter(iterable)
    if initializer is None:
        try:
            initializer = next(it)
        except StopIteration:
            raise TypeError('reduce() of empty sequence with no initial value')
    accum_value = initializer
    for x in it:
        step = function(accum_value, x)
        if step is not Reduced: # <-- here's where we can terminate early.
            accum_value = step
        else:
            return accum_value
    # Completing step will fire if needed.
    try:
        accum_value = function(accum_value)
    except:
        pass # <-- hack at moment because Python reducers don't take single
             #     arity like transducers.
    return accum_value


def compose(*fns):
    """Compose functions using reduce on splat.

    compose(f, g) reads 'f composed with g', or f(g(x))
    """
    return functools.reduce(lambda f,g: lambda x: f(g(x)), fns)

def transduce(transducer, reducer, start, coll):
    """Return the results of calling transduce on the reducing function,
    can compose transducers using compose defined above.

    Note: could possibly switch coll/start order if we want to match Python
    reduce instead of Clojure reduce.
    """
    return reduce(transducer(reducer), coll, start)

def map(f):
    """Transducer version of map."""
    def xducer(step):
        def _reduce(r=None, x=None):
            if x is None:
                return step(r)
            return step(r, f(x))
        return _reduce
    return xducer

def filter(pred):
    """Transducer version of filter."""
    def xducer(step):
        def _reduce(r=None, x=None):
            if x is None:
                return step(r)
            return step(r, x) if pred(x) else r
        return _reduce
    return xducer

def cat(step):
    """Cat helper function/transducer."""
    def _reduce(r=None, x=None):
        if x is None:
            return step(r)
        return functools.reduce(step, x, r)
    return _reduce

def mapcat(f):
    """Mapcat transducer."""
    return compose(map(f), cat)

def take(n):
    """Taking transducer."""
    def xducer(step):
        outer_vars = {"counter": 0} # <-- ugh, state in closures w/o
                                    #     nonlocal from Python 3 :(
        def _reduce(r=None, x=None):
            if x is None:
                return step(r)
            if outer_vars["counter"] < n:
                outer_vars["counter"] += 1
                return step(r, x)
            else:
                return Reduced
        return _reduce
    return xducer

def take_while(pred):
    def xducer(step):
        def _reduce(r=None, x=None):
            if x is None:
                return step(r)
            if pred(x):
                return step(r, x)
            else:
                return Reduced
        return _reduce
    return xducer

def drop(n):
    def xducer(step):
        outer = {"count": 0}
        def _reduce(r=None, x=None):
            if x is None:
                return step(r)
            if outer["count"] < n:
                outer["count"] += 1
                return r
            else:
                return step(r, x)
        return _reduce
    return xducer

def drop_while(pred):
    def xducer(step):
        outer = {"trigger": False}
        def _reduce(r=None, x=None):
            if x is None:
                return step(r)
            if outer["trigger"]:
                return step(r, x)
            elif not pred(x):
                outer["trigger"] = True
                return step(r, x)
            return r
        return _reduce
    return xducer

def take_nth(n):
    def xducer(step):
        outer = {"idx": 0}
        def _reduce(r=None, x=None):
            if x is None:
                return step(r)
            if outer["idx"] % n:
                outer["idx"] += 1
                return r
            else:
                outer["idx"] += 1
                return step(r, x)
        return _reduce
    return xducer

def replace(smap):
    def xducer(step):
        def _reduce(r=None, x=None):
            if x is None:
                return step(r)
            if x in smap:
                return step(r, smap[x])
            else:
                return step(r, x)
        return _reduce
    return xducer

def keep(pred):
    def xducer(step):
        def _reduce(r=None, x=None):
            if x is None:
                return step(r)
            res = pred(x)
            return step(r, res) if res is not None else r
        return _reduce
    return xducer

def remove(pred):
    def xducer(step):
        def _reduce(r=None, x=None):
            if x is None:
                return step(r)
            if not pred(x):
                return step(r, x)
            return r
        return _reduce
    return xducer

def keep_indexed(f):
    def xducer(step):
        outer = {"idx": 0}
        def _reduce(r=None, x=None):
            if x is None:
                return step(r)
            res = f(outer["idx"], x)
            outer["idx"] += 1
            return step(r, res) if res is not None else r
        return _reduce
    return xducer

def dedupe(step):
    outer = {}
    def _reduce(r=None, x=None):
        if x is None:
            return step(r)
        if "prev" not in outer:
            outer["prev"] = x
            return step(r, x)
        elif x != outer["prev"]:
            outer["prev"] = x
            return step(r, x)
        else:
            return r
    return _reduce

def partition_by(pred):
    """Need for completed may force OO implementation. Have to sleep on it.
    Alternatively could provide same arity structure as in Clojure."""
    def xducer(step):
        outer = {"last": False,
                 "temp": []}
        def _reduce(r=None, x=None):
            if x is None:
                return step(r, outer["temp"]) if outer["temp"] else step(r)
            if pred(x) == outer["last"]:
                outer["temp"].append(x)
                return r
            else:
                outer["last"] = pred(x)
                _temp = outer["temp"][:]
                outer["temp"] = [x]
                return step(r, _temp) if _temp else r
        return _reduce
    return xducer

def partition_all(n):
    def xducer(step):
        outer = {"temp": [],
                 "idx": 0}
        def _reduce(r=None, x=None):
            if x is None:
                return step(r, outer["temp"]) if outer["temp"] else step(r)
            if not outer["idx"] % n:
                outer["idx"] += 1
                _temp = outer["temp"][:]
                outer["temp"] = [x]
                return step(r, _temp) if _temp else r
            outer["temp"].append(x)
            outer["idx"] += 1
            return r
        return _reduce
    return xducer

def random_sample(prob):
    def xducer(step):
        def _reduce(r=None, x=None):
            if x is None:
                return step(r)
            if random() < prob:
                return step(r, x)
            return r
        return _reduce
    return xducer
