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
from __future__ import division
try:
    import __builtin__
except ImportError: # <-- hack for Python3
    import builtins as __builtin__
"""
This test suite should pass python3, python2, and pypy:

python tests/transducer_tests.py
python3 tests/transducer_tests.py
pypy tests/transducer_tests.py

If it doesn't pass all three, don't commit changes unless you _really_ know
what you are doing!
"""
from transducers import *
import unittest
from collections import deque
from fractions import Fraction

# helping reducers
from operator import add, mul

# list
def append(l, item):
    l.append(item)
    return l

# deques
def dright_append(d, item):
    d.append(item)
    return d

def dleft_append(d, item):
    d.appendleft(item)
    return d

# helping functions
fodd = lambda x: x%2
msq = lambda x: x*x

def onlyeven(x):
    """could be lambda x: x if x%2 == 0 else None"""
    if x%2 == 0:
        return x

def onlyeven_idx(i, x):
    if i%2 == 0:
        return x

def geometric_series(a, r):
    """An infinite series example w/generators."""
    power = 0
    yield a
    while True:
        power += 1
        yield a * r**power

def alternating_transducer(step):
    """Used to show compatibility w/transducer semantics."""
    outer = {"prev": 1}
    def alternate(r, x):
        sign = outer["prev"]
        outer["prev"] *= -1
        return step(r, sign*x)
    return alternate

class TransducerTests(unittest.TestCase):
    """
    These tests verify that Python tranducers return same or best match avail.
    compared to results in Clojure. Tests built with comparison against Clojure
    REPL 1.7_alpha2 for Transducer behavior, data structures/reducers matched
    as:

    Clojure conj/vector = Python append/list
    Clojure conj/list = Python dleft_append/deque
    """
    def test_map(self):
        self.assertEqual(transduce(map(lambda x: x**2),
                                  append, [], range(5)),
        # (transduce (map #(* %  %)) conj [] (range 5))
          [0, 1, 4, 9, 16])

    def test_filter(self):
        self.assertEqual(transduce(filter(lambda x: x%2 == 0),
                                  append, [], range(5)),
        # (transduce (filter even?) conj [] (range 5))
          [0, 2, 4])

    def test_cat(self):
        self.assertEqual(transduce(cat, append, [], [[1,2],[3,4]]),
        # (transduce cat conj [] [[1 2] [3 4]])
          [1, 2, 3, 4])

    def test_mapcat(self):
        self.assertEqual(transduce(mapcat(reversed),
                                   append, [], [[3, 2, 1], [5, 4]]),
        # (transduce (mapcat reverse) conj [] [[3 2 1] [5 4]])
          [1, 2, 3, 4, 5])

    def test_take(self):
        self.assertEqual(transduce(take(3), append, [], range(10)),
        # (transduce (take 3) conj [] (range 10))
          [0, 1, 2])

    def test_remove(self):
        self.assertEqual(transduce(remove(lambda x: x%2 == 0),
                                   append, [], range(10)),
        # (transduce (remove even?) conj [] (range 10))
          [1, 3, 5, 7, 9])

    def test_take_while(self):
        self.assertEqual(transduce(take_while(lambda x: x%2 == 0),
                                   append, [], [2, 4, 6, 7, 8]),
        # (transduce (take-while even?) conj [] [2 4 6 7 8])
          [2, 4, 6])

    def test_drop(self):
        self.assertEqual(transduce(drop(4), append, [], range(5)),
        # (transduce (drop 4) conj [] (range 5))
          [4])

    def test_drop_while(self):
        self.assertEqual(transduce(drop_while(lambda x: x%2 == 0),
                                   append, [], [2, 4, 6, 7, 8]),
        # (transduce (drop-while even?) conj [] [2 4 6 7 8])
          [7, 8])

    def test_take_nth(self):
        self.assertEqual(transduce(take_nth(3), append, [], range(20)),
        # (transduce (take-nth 3) conj [] (range 20))
          [0, 3, 6, 9, 12, 15, 18])

    def test_replace(self):
        self.assertEqual(transduce(replace({1:"ok"}), 
            append, [], (1, 3, 1, 5, 1, 7)),
        # (transduce (replace {1 "ok"}) conj [] '(1 3 1 5 1 7))
          ["ok", 3, "ok", 5, "ok", 7])

    def test_keep(self):
        self.assertEqual(transduce(keep(onlyeven), append, [], range(10)),
        # (transduce (keep #(if (even? %) %)) conj [] (range 10))
          [0, 2, 4, 6, 8])

    def test_keep_indexed(self):
        self.assertEqual(transduce(keep_indexed(onlyeven_idx), append, [], [1, 3, 5, 7]),
        # (transduce (keep-indexed #(if (even? %1) %2)) conj [] [1 3 5 7])
          [1, 5])

    def test_partition_by(self):
        self.assertEqual(transduce(partition_by(lambda x: x%2 == 0),
                                   append, [], [1, 3, 1, 4, 2, 1, 6]),
        # (transduce (partition-by even?) conj [] [1 3 1 4 2 1 6])
          [[1, 3, 1], [4, 2], [1], [6]])

    def test_partition_all(self):
        self.assertEqual(transduce(partition_all(4), append, [], range(15)),
        # (transduce (partition-all 4) conj [] (range 15))
          [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14]])

    def test_dedupe(self):
        self.assertEqual(transduce(dedupe, append, [],
                                   (1, 3, 1, 1, 2, 2, 2, 1, 4)),
        # (transduce (dedupe) conj [] '(1 3 1 1 2 2 2 1 4))
          [1, 3, 1, 2, 1, 4])

    def test_random_sample(self):
        """May extremely rarely fail."""
        counts = []
        n = 1000
        while len(counts) < 100:
            counts.append(len(
                transduce(random_sample(0.4), append, [], range(n))
                ))
        avg = sum((count/n for count in counts))/len(counts)
        self.assertTrue(abs(avg - 0.4) < 0.1) # <-- not an empirical threshold

    def test_big_comp(self):
        """We just want this one to run."""
        self.assertTrue(transduce(compose(mapcat(reversed),
                                 map(msq),
                                 filter(fodd),
                                 random_sample(0.20),
                                 partition_all(4),
                                 take(6)),
                         append, [],
                         [range(10000),
                          range(10000),
                          range(10000)]))

    def test_mf_correct(self):
        """Should be identical output to map and filter without transduction."""
        self.assertEqual([a for a in __builtin__.map(msq, 
                                     __builtin__.filter(fodd, range(10000)))],
                          transduce(compose(filter(fodd), map(msq)),
                          append, [], range(10000)))

    def test_mapcat(self):
        """Verify that mapcat works."""
        self.assertEqual(transduce(mapcat(reversed),
                         append, [], [[4,3,2], [7,6,5]]),
                         [2, 3, 4, 5, 6, 7])

    def test_frontappend(self):
        """Verify deque alternative reduction is correct (collection agnostic)."""
        self.assertEqual(transduce(compose(take(5), map(msq)),
                                   dleft_append, deque(), range(10)),
                                   deque([16, 9, 4, 1, 0]))

    def test_generator_function_input(self):
        """Test input of geometric series that would be infinite w/o short circuit."""
        self.assertEqual(transduce(take(3),
                                   add,
                                   Fraction(0, 1),
                                   geometric_series(Fraction(1, 1), Fraction(1, 2))),
                        Fraction(7, 4))

    def test_dedupe(self):
        """Test dedupe behavior for correctness."""
        self.assertEqual(transduce(dedupe, 
                                   append, [], 
                                   [1, 1, 2, 3, 4, 4, 4, 5, 1]),
                                   [1, 2, 3, 4, 5, 1])

    def test_string_to_ints(self):
        """Transduce from string into sum of ints."""
        self.assertEqual(transduce(compose(map(ord), take(10)),
                                   add, 0, "This is just some string!"),
                                   915)

    def test_partition_all_map(self):
        """Test map container type to generator partitions."""
        self.assertEqual(transduce(compose(partition_all(4), map(list)),
                         append, [], range(10)),
                         [[0,1,2,3],[4,5,6,7],[8,9]])

    def test_compatibiliy_with_proper_transducers(self):
        """Verifies we can transduce by composing reducers."""
        self.assertEqual(transduce(take(5),
                         alternating_transducer(append),
                         [],
                         geometric_series(1, 2)),
            [1, -2, 4, -8, 16])

    def test_into_list(self):
        """Verifies we can transduce using into."""
        self.assertEqual(into([], map(lambda x: x*2), range(10)),
                         [0, 2, 4, 6, 8, 10, 12, 14, 16, 18])
        self.assertEqual(into(deque(), map(lambda x: x*2), range(10)),
                         deque([0, 2, 4, 6, 8, 10, 12, 14, 16, 18]))

    def test_shortcircuit(self):
        """Makes sure we terminate when take is later in the chain."""
        self.assertTrue(transduce(compose(map(lambda x: x*x),
                                          filter(lambda x:x%2),
                                          take(10)),
                                          append,
                                          [],
                                          geometric_series(Fraction(1,1),
                                                           Fraction(1,2))))

    def test_completion_forward(self):
        """Make sure partition_all works when short circuited by take."""
        self.assertEqual(transduce(compose(take(5), partition_all(4)), 
                                  append, [], range(10)),
                                  [[0, 1, 2, 3], [4]])

    def test_completion_backward(self):
        """Make sure we completed partition_by when short circuiting by take
        later."""
        self.assertEqual(transduce(compose(partition_by(fodd), take(3)),
                         append, [], [1, 1, 1, 2, 2, 2, 3]),
                         [[1, 1, 1], [2, 2, 2], [3]])

    def two_completing_steps(self):
        """Make sure two completing steps fire in correct order."""
        self.assertEqual(transduce(compose(partition_by(fodd), partition_all(2)),
                                   append, [], range(10)),
                         [[[0], [1]], [[2], [3]], [[4], [5]], [[6], [7]], [[8], [9]]])


# Verbose tests to verify transducer correctness
if __name__ == "__main__":
    unittest.main()
