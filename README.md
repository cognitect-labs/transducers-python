# Transducers in Python

There are some competing concerns at the moment addressed by the test
implementations included here so far:

transducers.py is a correct near-transliteration implemention in Python
    which is not particularly performant (about 5x slower than typical Pythonic
    solution)

cyduce.pyx demonstrates (mainly for benchmarking) performance gains for going
    to C given function call overhead in native Python solutions, but cannot
    present a realistic API (except for applications written in Cython).

genducers.py shows the more Pythonic solution, utilizing generators and
    composing generators (chaining them together) followed by reducing over
    them, but the implementation is not really transducers (although it seems
    able to present the same API from preliminary work). More performant than
    transducers.py
