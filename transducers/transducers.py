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
This is an implementation of Rich Hickey's Transducers from Clojure in Python.
It uses functional programming in Python and an alternative reduce which
recognizes Reduced, a sentinel wrapper with a value that can be extracted to
signal early termination.

Composed transducers result in a reversed composed process. E.g.,

> compose(map(f), filter(g))

Will apply f to the reduction step before filtering with g. This comes out of
the composition of transducers naturally as a transducer inserts its
transformation before the reducing function it accepts as an argument.

Transducers can be called with transduce or transduce into a collection with
into.
"""
class Missing(object):
    """Only for 'is' comparison to simplify arity testing. This is because None
    is a legal argument differing from 'Not supplied.'"""
    pass


class Reduced(object):
    """Sentinel wrapper from which terminal value can be retrieved. If received
    by transducers.reduce, will signal early termination."""
    def __init__(self, val):
        self.val = val


def ensure_reduced(x):
    return x if isinstance(x, Reduced) else Reduced(x)

def unreduced(x):
    return x.val if isinstance(x, Reduced) else x

def reduce(function, iterable, initializer=Missing):
    """
    For loop impl of reduce in Python that honors sentinal wrapper Reduced and
    uses it to signal early termination.
    """
    if initializer is Missing:
        accum_value = function() # 0 arity initializer.
    else:
        accum_value = initializer

    for x in iterable:
        accum_value = function(accum_value, x)
        if isinstance(accum_value, Reduced): # <-- here's where we can terminate early.
            return accum_value.val
    return accum_value


def compose(*fns):
    """Compose functions using reduce on splat.

    compose(f, g) reads 'f composed with g', or f(g(x))

    Note: order of inner function application with transducers is inverted from
    the composition of the transducers.
    """
    return functools.reduce(lambda f,g: lambda x: f(g(x)), fns)


def transduce(xform, f, start, coll=Missing):
    """Return the results of calling transduce on the reducing function,
    can compose transducers using compose defined above.
    """
    if coll is Missing:
        return transduce(xform, f, f(), start)
    reducer = xform(f)
    ret = reduce(reducer, coll, start)
    return reducer(ret) # completing step moved to here

# Transducers
def map(f):
    """Transducer version of map, returns f(item) with each reduction step."""
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
    """Mapcat transducer - maps to a collection then cats item into one less
    level of nesting."""
    return compose(map(f), cat)

def take(n):
    """Takes n values from a collection."""
    def _take_xducer(step):
        outer_vars = {"counter": n}
        def _take_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            n = outer_vars["counter"]
            outer_vars["counter"] -= 1
            r = step(r, x) if n > 0 else r
            return ensure_reduced(r) if outer_vars["counter"] <= 0 else r
        return _take_step
    return _take_xducer

def take_while(pred):
    """Takes while a condition is true. Note that take_while will take the
    first input that tests false, so be mindful of mutable input sources."""
    def _take_while_xducer(step):
        def _take_while_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            return step(r, x) if pred(x) else Reduced(r)
        return _take_while_step
    return _take_while_xducer

def drop(n):
    """Drops n items from beginning of input sequence."""
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
    """Drops values so long as a condition is true."""
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
    """Takes every nth item from input values."""
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
    """Replaces keys in smap with corresponding values."""
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
    """Keep pred items for which pred does not return None."""
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
    """Remove anything that satisfies pred."""
    def _remove_xducer(step):
        def _remove_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            return step(r, x) if not pred(x) else r
        return _remove_step
    return _remove_xducer

def keep_indexed(f):
    """Keep values where f does not return None. f for keep indexed is a
    function that takes both index and value as inputs."""
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
    """Removes duplicatees that occur in order. Accepts first inputs through
    and drops subsequent duplicates."""
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
    """Split inputs into lists by starting a new list each time the predicate
    passed in evaluates to a different condition (true/false) than what holds
    for the present list."""
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
                _r =  unreduced(step(r, _temp))
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
                if not isinstance(ret, Reduced):
                    outer["temp"].append(x)
                return ret

        return _partition_by_step
    return _partition_by_xducer

def partition_all(n):
    """Splits inputs into lists of size n."""
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
                _r =  unreduced(step(r, _temp))
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
    """Has prob probability of returning each input it receives."""
    def _random_sample_xducer(step):
        def _random_sample_step(r=Missing, x=Missing):
            if r is Missing: return step()
            if x is Missing:
                return step(r)
            return step(r, x) if random() < prob else r
        return _random_sample_step
    return _random_sample_xducer


def append(r=Missing, x=Missing):
    """Appender used by into. Will work with lists, deques, or anything with
    an appender."""
    if r is Missing: return []
    if x is Missing: return r
    r.append(x)
    return r

def into(target, xducer, coll):
    """Transduces items from coll into target.
    :TODO: Write improved dispatch for collections?"""
    return transduce(xducer, append, target, coll)

def eduction(xf, coll):
    """Return a generator with transform applied. Not implemented."""
    raise NotImplementedError
