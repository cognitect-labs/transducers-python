# transducers-python

[Transducers](http://clojure.org/transducers) are composable algorithmic transformations. They are independent from the context of their input and output sources and specify only the essence of the transformation in terms of an individual element. Because transducers are decoupled from input or output sources, they can be used in many different processes - collections, streams, channels, observables, etc. Transducers compose directly, without awareness of input or creation of intermediate aggregates.

In Python you can transduce anything you can iterate over (the implementation of reduce included uses a for loop). This includes generators and coroutines in addition to the vast majority of Python collections. See below for an example of transducing over a generator.

For more information about Clojure transducers and transducer semantics see the introductory [blog post](http://blog.cognitect.com/blog/2014/8/6/transducers-are-coming) and this [video](https://www.youtube.com/watch?v=6mTbuzafcII).

transducers-python is brought to you by [Cognitect Labs](http://cognitect-labs.github.io/).

## Installation

    pip install --use-wheel --pre transducers

## Compatibility

transducers-python is compatible with Python 2.7.8, Python 3.X, and [PyPy](http://pypy.org/). It may be compatible with other Python Implementations as well.

## Documentation

API documentation can be found [here](https://pythonhosted.org/transducers/index.html).

## Usage

```python
import transducers as T
from fractions import Fraction

def geometric_series(a, r):
    power = 0
    yield a
    while True:
        power += 1
        yield a * r**power

T.transduce(T.compose(T.take(3), T.map(float)),
            T.append,
            [],
            geometric_series(Fraction(1, 1), Fraction(1, 2)))

# > [1.0, 0.5, 0.25]
```

For more examples of use, see the test suite tests/transducer_tests.py.

## Contributing

This library is open source, developed internally by [Cognitect](http://cognitect.com). Issues can be filed using [GitHub Issues](https://github.com/cognitect-labs/transducers-python/issues).

This project is provided without support or guarantee of continued development.
Because transducers-python may be incorporated into products or client projects, we prefer to do development internally and do not accept pull requests or patches.

## Copyright and License

Copyright © 2014 Cognitect

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
