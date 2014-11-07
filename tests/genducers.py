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
"""
Genducers in Python are quasi-transducers that have identical semantics in
call to transduce. I.e., they can be composed with a left-to-right processing
chain in the first argument to genduce.

These are only for benchmarking and not supported for other uses. They do not
pass all transducer tests for nontrivial completion.
"""
# Build this to reduce over the final generator, compose to get generator.
from functools import partial, reduce
from random import random

def compose(*fns):
    """Compose functions left to right - allows generators to compose with same
    order as Clojure style transducers in first argument to transduce."""
    return reduce(lambda f,g: lambda x: g(f(x)), fns)

def rcompose(*fns):
    """Right compose for stack, left compose to traverse stack afterwards for
    Clojure style transducers. This is an _intended_ pun on 'reducer compose',
    i.e., you should use it to compose against the reducer argument to
    transduce if you want to use a Clojure style transducer."""
    return reduce(lambda f,g: lambda x: f(g(x)), fns)

def take(n):
    """Returns n entites from collection."""
    def generator(coll):
        for i, item in enumerate(coll):
            if i >= n:
                break
            yield item
    return generator

def cat(coll):
    """Cats items from nested colls into the coll, traverses one level."""
    for item in coll:
        for subitem in item:
            yield subitem

def map(f):
    """"""
    def generator(coll):
        for x in coll:
            yield f(x)
    return generator

def filter(pred):
    """Filter, for composition with generators that take coll as an argument."""
    def generator(coll):
        for x in coll:
            if pred(x):
                yield x
    return generator

def remove(pred):
    """Remove any item from collection on traversal if that item meets condition
    specified in pred."""
    def generator(coll):
        for item in coll:
            if not pred(item):
                yield item
    return generator

def take_while(pred):
    """Keep taking until pred is false."""
    def generator(coll):
        for item in coll:
            if pred(item):
                yield item
            else:
                break
    return generator

def drop(n):
    """Drop n items from collection (first in dropped)."""
    def generator(coll):
        for i, item in enumerate(coll):
            if i >= n:
                yield item
    return generator

def drop_while(pred):
    """Drop so long as pred is true -- then yield values even if pred becomes
    true again (triggered once)."""
    def generator(coll):
        trigger = False
        for item in coll:
            if trigger:
                yield item
            elif not pred(item):
                trigger = True
                yield item
    return generator

def take_nth(n):
    """Take each nth item from a collection, always start on first (0 idx)."""
    def generator(coll):
        for i, item in enumerate(coll):
            if not i % n:
                yield item
    return generator

def replace(smap):
    """With dictionary argument, subsitute each instance of key with value."""
    def generator(coll):
        for item in coll:
            if item in smap:
                yield smap[item]
            else:
                yield item
    return generator

def keep(pred):
    """Keep only items that do not return None when pred is called. This is for
    functions that only return values in certain cases, or which return None
    for their false value."""
    def generator(coll):
        for item in coll:
            res = pred(item)
            if res is not None:
                yield res
    return generator

def keep_indexed(f):
    """For each enumerated collection, we can use a function that takes its
    index and the item to determine whether to keep the result and if so what
    form to keep it in."""
    def generator(coll):
        for idx, item in enumerate(coll):
            res = f(idx, item)
            if res is not None:
                yield res
    return generator

def dedupe(coll):
    """Remove consecutive duplicates."""
    prev = next(coll)
    yield prev
    for item in coll:
        if item != prev:
            prev = item
            yield item

def partition_by(pred):
    """If pred changes from True to False or vice versa, we break up the
    results from that boundary into their own sub-collections (lists)."""
    def generator(coll):
        last = False
        temp = []
        for item in coll:
            if pred(item) == last:
                temp.append(item)
            else:
                if temp:
                    yield temp
                last = pred(item)
                temp = [item]
        if temp:
            yield temp
    return generator

def partition_all(n):
    """Partition a collection into sub-collections (lists) of size n."""
    def generator(coll):
        temp = []
        for i, item in enumerate(coll, 1):
            temp.append(item)
            if not i % n:
                yield temp
                temp = []
        if temp:
            yield temp
    return generator

def random_sample(prob):
    """Transducer that has a prob (0.0-1.0) of returning item per item in
    collection."""
    def generator(coll):
        for item in coll:
            if random() < prob:
                yield item
    return generator

def mapcat(f):
    """Map a function to sub-collections then cat the subcollections into a
    collection at the next level up (traverses one level)."""
    return compose(map(f), cat)

def transduce(generator, reducer, start, coll):
    """Function that can be used to transduce over a collection. That is, it
    transforms the collection as the collection traverses the reduction process
    per step through the process."""
    return reduce(reducer, generator((a for a in coll)), start)

def into(target_coll, generator, coll):
    """Given constructing function or instance of a target collection,
    transforms input collection through generator and outputs a new
    collection of type target_collection.

    :TODO:
    We could eliminate the niceness around accepting both a constructor and an
    instance, Clojure only accepts an instance.
    """
    return type(target_coll)(generator(coll)) \
           if not isinstance(target_coll, type) \
           else target_coll(generator(coll))

def eduction(xf, coll):
    """Apply generator to coll to produce an iterable transforming collection.
    This is basically just to allow semantic equivalence to Clojure's eduction.
    """
    return xf(coll)
