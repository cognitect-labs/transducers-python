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
The transducers backend is less performant but consistent with the semantics
of transducers in Clojure. It deliberately avoids an OO layer and is meant to
be considered an alternative to both a (not implemented)  OO and generator
backend.
"""
class Reduced(object):
    """Only for 'is' comparison to signal early termination of reduce."""
    pass

class Missing(object):
    """Only for 'is' comparison to simplify arity testing."""
    pass

def reduce(function, iterable, initializer=Missing):
    """Using Python documentation's function as base, adding check for
    reduced state and call for final completion step.
    """
    accum_value = function() if initializer is Missing else initializer
    if initializer is Missing:
        accum_value = function() # 0 arity initializer.
    else:
        accum_value = initializer

    for x in iterable:
        step = function(accum_value, x)
        if step is not Reduced: # <-- here's where we can terminate early.
            accum_value = step  #     presently buggy in composition.
        else:
            break
    # Completing step will fire if needed.
    try:
        last_step = function(accum_value)
    # Except this is append a reducer a la append  and it doesn't have arity 1
    except TypeError:
        return accum_value
    return accum_value if last_step is Reduced else last_step


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
        def _reduce(r, x=Missing):
            return step(r) if x is Missing else step(r, f(x))
        return _reduce
    return xducer

def filter(pred):
    """Transducer version of filter."""
    def xducer(step):
        def _reduce(r, x=Missing):
            if x is Missing:
                return step(r)
            return step(r, x) if pred(x) else r
        return _reduce
    return xducer

def cat(step):
    """Cat helper function/transducer."""
    def _reduce(r, x=Missing):
        return step(r) if x is Missing else functools.reduce(step, x, r)
    return _reduce

def mapcat(f):
    """Mapcat transducer."""
    return compose(map(f), cat)

def take(n):
    """Taking transducer."""
    def xducer(step):
        outer_vars = {"counter": 0}
        def _reduce(r, x=Missing):
            if x is Missing:
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
        def _reduce(r, x=Missing):
            if x is Missing:
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
        def _reduce(r, x=Missing):
            if x is Missing:
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
        def _reduce(r, x=Missing):
            if x is Missing:
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
        def _reduce(r, x=Missing):
            if x is Missing:
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
        def _reduce(r, x=Missing):
            if x is Missing:
                return step(r)
            if x in smap:
                return step(r, smap[x])
            else:
                return step(r, x)
        return _reduce
    return xducer

def keep(pred):
    def xducer(step):
        def _reduce(r, x=Missing):
            if x is Missing:
                return step(r)
            res = pred(x)
            return step(r, res) if res is not None else r
        return _reduce
    return xducer

def remove(pred):
    def xducer(step):
        def _reduce(r, x=Missing):
            if x is Missing:
                return step(r)
            return step(r, x) if not pred(x) else r
        return _reduce
    return xducer

def keep_indexed(f):
    def xducer(step):
        outer = {"idx": 0}
        def _reduce(r, x=Missing):
            if x is Missing:
                return step(r)
            res = f(outer["idx"], x)
            outer["idx"] += 1
            return step(r, res) if res is not None else r
        return _reduce
    return xducer

def dedupe(step):
    outer = {}
    def _reduce(r, x=Missing):
        if x is Missing:
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
    """Well, don't need OO but partition* transducers are slowest by far."""
    def xducer(step):
        outer = {"last": False,
                 "temp": []}
        def _reduce(r, x=Missing):
            if x is Missing:
                return step(r, outer["temp"]) if outer["temp"] else step(r)
            if pred(x) == outer["last"]:
                outer["temp"].append(x)
                return r
            else:
                outer["last"] = pred(x)
                _temp = outer["temp"][:]
                del outer["temp"][:]
                outer["temp"].append(x)
                return step(r, _temp) if _temp else r
        return _reduce
    return xducer

def partition_all(n):
    def xducer(step):
        outer = {"temp": [],
                 "idx": 0}
        def _reduce(r, x=Missing):
            if x is Missing:
                return step(r, outer["temp"]) if outer["temp"] else step(r)
            if not outer["idx"] % n:
                outer["idx"] += 1
                _temp = outer["temp"][:]
                del outer["temp"][:]    # cheaper than getting
                outer["temp"].append(x) # a new list.
#                outer["temp"] = [x]
                return step(r, _temp) if _temp else r
            outer["temp"].append(x)
            outer["idx"] += 1
            return r
        return _reduce
    return xducer

def random_sample(prob):
    def xducer(step):
        def _reduce(r, x=Missing):
            if x is Missing:
                return step(r)
            return step(r, x) if random() < prob else r
        return _reduce
    return xducer

def _append(l, x):
    """Local append for into to use."""
    l.append(x)
    return l

def into(target, xducer, coll):
    """Only honors things that append at the moment."""
    return transduce(xducer, _append, type(target)(), coll)

def eduction(xf, coll):
    """Return a generator with transform applied. Not implemented."""
    pass
