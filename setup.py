from setuptools import setup, find_packages
#from Cython.Build import cythonize

# This isn't a real setup file yet, just the hooks for Cythonize.
setup(name="transducers",
#      version="0.4" + revision, <-- need to hook up
      description="Transducer semantics for Python generators.",
      author="Cognitect",
      url="https://github.com/cognitect-labs/transducers-python",
      packages=find_packages())
 #     ext_modules = cythonize("transducers/cgenducers.pyx"))
