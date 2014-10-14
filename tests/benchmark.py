from transducers import transducers as T
from transducers import genducers as G
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
                      X.take(10000000),
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

runs = 100
T_deltas = [run_tests(T) for x in range(runs)]
G_deltas = [run_tests(G) for x in range(runs)]
T_mean = sum(T_deltas) / runs
G_mean = sum(G_deltas) / runs

print("Average for Generators: " + str(G_mean) + " ms.")
print("Average for Transducers: " + str(T_mean) + " ms.")

