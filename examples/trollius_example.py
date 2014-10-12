"""
These are just scratches leading to a better example.
"""
import trollius as asyncio
from trollius import From

from tests.transducer_tests import geometric_series
from fractions import Fraction
from transducers import filter, take, compose, map, partition_all
from time import sleep

@asyncio.coroutine
def basic_geometric_series():
    """Sends terms on delay."""
    for a in geometric_series(Fraction(1,1), Fraction(1,2)):
        sleep(1)
        yield a

@asyncio.coroutine
def list_xduced_terms(n):
    """transduces terms on delay."""
    xducer = compose(map(lambda x:x*x), partition_all(n), take(10))
    for a in xducer(basic_geometric_series()):
        print(a)
        yield From(asyncio.sleep(1))

loop = asyncio.get_event_loop()
loop.run_until_complete(list_xduced_terms(3))
