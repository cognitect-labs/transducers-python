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
from transducers import transducers as T
from tests import genducers as G
from tests.transducer_tests import append
import time

scale = 10

def run_tests(X):
    t = time.time()
    xducer = (X.compose(
                      X.mapcat(reversed),
                      X.map(lambda x: x*x),
                      X.filter(lambda x: x%2),
                      X.take_nth(4),
                      X.dedupe,
                      X.random_sample(0.70),
                      X.partition_all(4),
                      X.take(4 * scale**3),
                      X.mapcat(reversed),
                      X.drop_while(lambda x: x < 20),
                      X.remove(lambda x: x%7),
                      X.replace({217: 271}),
                      X.partition_by(lambda x: x < 200)
                         ))
    X.transduce(xducer,
              append, [],
              [range(10000)] * scale)
    tt = time.time()
    return tt*1000.0 - t*1000.0

def benchmark_one(X, xduc, input=None, runs=100):
    """For passing a bunch of transducers in."""
    if not input:
        input = range(10000) * scale

    xducer = eval(xduc)

    def test():
        t = time.time()
        X.transduce(xducer, append, [], input)
        tt = time.time()
        return tt*1000.0 - t*1000.0

    avg = sum([test() for x in range(runs)]) / runs
    print("Avg. time for " + X.__name__ + " with " + xduc + \
          " is: " + str(avg))

if __name__ == "__main__":
    # Define some transducer scenarios. Could comp these through permutations,
    # if we want to go that route.
    xducers = {"map(lambda x: x*x)": None,
               "filter(lambda x: x%2)": None,
               "take(10000)": None,
               "partition_by(lambda x: x%2)": range(100) * scale,
               "partition_all(10)": range(1000) * scale,
               "mapcat(reversed)": [range(1000)] * scale,
               "cat": [range(1000)] * scale,
               "take_while(lambda x: x < 1000)": None,
               "remove(lambda x: x % 4)": None,
               "drop(1000)": None,
               "drop_while(lambda x: x < 1500)": None,
               "take_nth(4)": None,
               "replace({0:1, 100:200, 1000:500})": None,
               "keep(lambda x: x if x > 100 else None)": None,
               "keep_indexed(lambda i, x: i*x if i%4 else None)": None,
               "dedupe": [1,1,1, 3,3,3, 2,4,2,4, 1,1,1] * scale*scale,
               "random_sample(0.4)": None}

    # Run benchmarks for whole set of transducers per tranducer
    for xduc, input in xducers.items():
        benchmark_one(T, "T."+xduc, input)
        benchmark_one(G, "G."+xduc, input)

    # Keep test for big compose for now...
    runs = 100
    T_deltas = [run_tests(T) for x in range(runs)]
    G_deltas = [run_tests(G) for x in range(runs)]
    T_mean = sum(T_deltas) / runs
    G_mean = sum(G_deltas) / runs

    print("Average for large compose for Generators: " + str(G_mean) + " ms.")
    print("Average for large compose for Transducers: " + str(T_mean) + " ms.")
