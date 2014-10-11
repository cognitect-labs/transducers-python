"""
Genducers in Python are pseudo-transducers that have identical semantics in
call to genduce (analogous to call to transduce). I.e., they can be composed
with a left-to-right processing chain in the first argument to genduce.

:TODO:
    Need to investigate speedup options from itertools, etc. These are mostly
    naive imperative implementations of generators, builtins from itertools
    when available (e.g. dropwhile, takewhile) are probably faster.
 
    Tests to determine equivalence with transducers (in tests/)

    Tests to determine input and output type/context capabilities.
"""
# Build this to reduce over the final generator, compose to get generator.
from functools import partial, reduce
from random import random

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


def remove(pred):
    """Remove genducer."""
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
                raise StopIteration
    return generator

def drop(n):
    """Drop until n"""
    def generator(coll):
        for i, item in enumerate(coll):
            if i >= n:
                yield item
    return generator

def drop_while(pred):
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
    def generator(coll):
        for i, item in enumerate(coll):
            if not i % n:
                yield item
    return generator

def replace(smap):
    def generator(coll):
        for item in coll:
            if item in smap:
                yield smap[item]
            else:
                yield item
    return generator

def keep(pred):
    def generator(coll):
        for item in coll:
            res = pred(item)
            if res is not None:
                yield res
    return generator

def keep_indexed(f):
    def generator(coll):
        for idx, item in enumerate(coll):
            res = f(idx, item)
            if res is not None:
                yield res
    return generator

def dedupe(coll):
    prev = next(coll)
    yield prev
    for item in coll:
        if item != prev:
            prev = item
            yield item

def partition_by(pred):
    def generator(coll):
        last = False
        temp = []
        for item in coll:
            if pred(item) == last:
                temp.append(item)
            else:
                yield (a for a in temp)
                temp = [item]
                last = pred(item)
    return generator

def partition_all(n):
    def generator(coll):
        temp = []
        for i, item in enumerate(coll, 1):
            temp.append(item)
            if not i % n:
                yield (a for a in temp)
                temp = []
        if temp:
            yield (a for a in temp)
    return generator

def random_sample(prob):
    def generator(coll):
        for item in coll:
            if random() < prob:
                yield item
    return generator

def mapcatting(f):
    return compose(mapping(f), cat)


def transduce(generator, reducer, start, coll):
    return reduce(reducer, generator((a for a in coll)), start)
