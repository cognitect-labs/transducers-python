from distutils.core import setup
from Cython.Build import cythonize

# This isn't a real setup file yet, just the hooks for Cythonize.
setup(ext_modules = cythonize("transducers/cyduce.pyx"))
