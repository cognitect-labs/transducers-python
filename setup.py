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
