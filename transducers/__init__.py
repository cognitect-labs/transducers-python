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

# Uncomment this line and comment line below to test Cython.
# -- Cython only compatible with version of Python built against,
# -- not compatible with PyPy.
# from . import cgenducers as genducers
from . import genducers
from .genducers import *

# -- uncomment these lines to switch backend to transducers a la Clojure
#from . import transducers
#from .transducers import *
