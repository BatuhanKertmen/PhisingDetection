import time

tic_1 = time.perf_counter()

def square(x):
    print(x ** 2)

from joblib import Parallel, delayed
a = Parallel(n_jobs=10000, prefer="threads")(delayed(square)(i) for i in range(10000))


print(a)

toc_1 = time.perf_counter()

print(toc_1 - tic_1)
