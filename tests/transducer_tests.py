import unittest
from transducers import *
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

def geometric_series(a, r):
    power = 0
    yield a
    while True:
        power += 1
        yield a * r**power

class TransducerTests(unittest.TestCase):
    def test_big_comp(self):
        """We just want this one to run."""
        self.assertTrue(transduce(compose(mapcatting(reversed),
                                 mapping(msq),
                                 filtering(fodd),
                                 random_sample(0.20),
                                 partition_all(4),
                                 taking(6)),
                         append, [],
                         [range(10000),
                          range(10000),
                          range(10000)]))

    def test_mf_correct(self):
        """Should be identical output to map and filter without transduction."""
        self.assertEqual(map(msq, filter(fodd, range(10000))),

                transduce(compose(filtering(fodd), mapping(msq)),
                          append, [], range(10000)))

    def test_mapcatting(self):
        """Verify that mapcatting works."""
        self.assertEqual(transduce(mapcatting(reversed),
                         append, [], [[4,3,2], [7,6,5]]),
                         [2, 3, 4, 5, 6, 7])

    def test_frontappend(self):
        """Verify deque alternative reduction is correct (collection agnostic)."""
        self.assertEqual(transduce(compose(taking(5), mapping(msq)),
                                   dleft_append, deque(), range(10)),
                                   deque([16, 9, 4, 1, 0]))

    def test_generator_function_input(self):
        """Test input of geometric series that would be infinite w/o short circuit."""
        self.assertEqual(transduce(taking(3),
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
        self.assertEqual(transduce(compose(mapping(ord), taking(10)),
                                   add, 0, "This is just some string!"),
                                   915)

    def test_partition_all_mapping(self):
        """Test mapping container type to generator partitions."""
        self.assertEqual(transduce(compose(partition_all(4), mapping(list)),
                         append, [], range(10)),
                         [[0,1,2,3],[4,5,6,7],[8,9]])

# Verbose tests to verify transducer correctness
if __name__ == "__main__":
    unittest.main()
