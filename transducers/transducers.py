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
    def __init__(self, x):
        self.x = x
    def _repr__(self):
        return x
    """Only for 'is' comparison to signal early termination of reduce."""

class Missing(object):
    """Only for 'is' comparison to simplify arity testing. This us because None
    is a legal argument differing from 'Not supplied.'"""
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
        if isinstance(step, Reduced): # <-- here's where we can terminate early.
            return step
        else:
            break
    return accum_value


def compose(*fns):
    """Compose functions using reduce on splat.

    compose(f, g) reads 'f composed with g', or f(g(x))
    """
    return functools.reduce(lambda f,g: lambda x: f(g(x)), fns)

def transduce(xform, f, start, coll=Missing):
    """Return the results of calling transduce on the reducing function,
    can compose transducers using compose defined above.

    Note: could possibly switch coll/start order if we want to match Python
    reduce instead of Clojure reduce.
    """
    if coll is Missing:
        return transduce(xform, f, f(), start)
    reducer = xform(f)
    ret = reduce(reducer, coll, start)
    return reducer(ret) # completing step moved to here

def map(f):
    """Transducer version of map."""
    def _map_xducer(step):
        def _map_step(r=Missing, x=Missing):
            if r is Missing: return step()
            return step(r) if x is Missing else step(r, f(x))
        return _map_step
    return _map_xducer

def filter(pred):
    """Transducer version of filter."""
    def _filter_xducer(step):
        def _filter_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            return step(r, x) if pred(x) else r
        return _filter_step
    return _filter_xducer

def cat(step):
    """Cat transducers (will cat items from nested lists, e.g.)."""
    def _cat_step(r=Missing, x=Missing):
        if r is Missing: return step()
        return step(r) if x is Missing else functools.reduce(step, x, r)
    return _cat_step

def mapcat(f):
    """Mapcat transducer."""
    return compose(map(f), cat)

def take(n):
    """Taking transducer."""
    def _take_xducer(step):
        outer_vars = {"counter": 1}
        def _take_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            if outer_vars["counter"] < n:
                outer_vars["counter"] += 1
                return step(r, x)
            else:
                return Reduced(step(r, x))
        return _take_step
    return _take_xducer

def take_while(pred):
    def _take_while_xducer(step):
        def _take_while_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            if pred(x):
                return step(r, x)
            else:
                return Reduced(r)
        return _take_while_step
    return _take_while_xducer

def drop(n):
    def _drop_xducer(step):
        outer = {"count": 0}
        def _drop_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            if outer["count"] < n:
                outer["count"] += 1
                return r
            else:
                return step(r, x)
        return _drop_step
    return _drop_xducer

def drop_while(pred):
    def _drop_while_xducer(step):
        outer = {"trigger": False}
        def _drop_while_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            if outer["trigger"]:
                return step(r, x)
            elif not pred(x):
                outer["trigger"] = True
                return step(r, x)
            return r
        return _drop_while_step
    return _drop_while_xducer

def take_nth(n):
    def _take_nth_xducer(step):
        outer = {"idx": 0}
        def _take_nth_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            if outer["idx"] % n:
                outer["idx"] += 1
                return r
            else:
                outer["idx"] += 1
                return step(r, x)
        return _take_nth_step
    return _take_nth_xducer

def replace(smap):
    def _replace_xducer(step):
        def _replace_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            if x in smap:
                return step(r, smap[x])
            else:
                return step(r, x)
        return _replace_step
    return _replace_xducer

def keep(pred):
    def _keep_xducer(step):
        def _keep_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            res = pred(x)
            return step(r, res) if res is not None else r
        return _keep_step
    return _keep_xducer

def remove(pred):
    def _remove_xducer(step):
        def _remove_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            return step(r, x) if not pred(x) else r
        return _remove_step
    return _remove_xducer

def keep_indexed(f):
    def _keep_indexed_xducer(step):
        outer = {"idx": 0}
        def _keep_indexed_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            res = f(outer["idx"], x)
            outer["idx"] += 1
            return step(r, res) if res is not None else r
        return _keep_indexed_step
    return _keep_indexed_xducer

def dedupe(step):
    outer = {}
    def _dedupe_step(r=Missing, x=Missing):
        if r is Missing: return step()
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
    return _dedupe_step

def partition_by(pred):
    """Well, don't need OO but partition* transducers are slowest by far."""
    def _partition_by_xducer(step):

        outer = {"last": Missing,
                 "temp": []}

        def _partition_by_step(r=Missing, x=Missing):
            if r is Missing: return step()

            # arity 1 - called on completion. 
            if x is Missing:
                if not outer["temp"]:
                    return r
                _temp = outer["temp"][:]
                del outer["temp"][:]
                _r =  step(r, _temp)
                return step(_r)

            # arity 2 - normal step.
            past_val = outer["last"]
            present_val = pred(x)
            outer["last"] = present_val
            if past_val is Missing or present_val == past_val:
                outer["temp"].append(x)
                return r
            else:
                _temp = outer["temp"][:]
                del outer["temp"][:]
                ret = step(r, _temp)
                if ret is not Reduced:
                    outer["temp"].append(x)
                return ret

        return _partition_by_step
    return _partition_by_xducer

def partition_all(n):
    def _partition_all_xducer(step):
        outer = {"temp": []}

        def _partition_all_step(r=Missing, x=Missing):
            if r is Missing: return step()

            # arity 1: called on completion.
            if x is Missing:
                if not outer["temp"]:
                    return r
                _temp = outer["temp"][:]
                del outer["temp"][:]
                _r =  step(r, _temp)
                return step(_r)

            # arity 2: called w/each reduction step.
            outer["temp"].append(x)
            if len(outer["temp"]) == n:
                _temp = outer["temp"][:]
                del outer["temp"][:]
                return step(r, _temp)
            return r

        return _partition_all_step
    return _partition_all_xducer

def random_sample(prob):
    def _random_sample_xducer(step):
        def _random_sample_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            return step(r, x) if random() < prob else r
        return _random_sample_step
    return _random_sample_xducer

def _append(l=Missing, x=Missing):
    """Local append for into to use."""
    if l is Missing: return []
    if x is Missing: return l
    l.append(x)
    return l

def into(target, xducer, coll):
    """Only honors things that append at the moment."""
    return transduce(xducer, _append, type(target)(), coll)

def eduction(xf, coll):
    """Return a generator with transform applied. Not implemented."""
    pass
