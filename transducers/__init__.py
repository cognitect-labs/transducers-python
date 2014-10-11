# Uncomment this line and comment line below to test Cython.
# -- Cython only compatible with version of Python built against,
# -- not compatible with PyPy.
# from . import cgenducers as genducers
from . import genducers
from .genducers import *
