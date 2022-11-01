from timeit import timeit


class Benchmark:
    def __init__(self, stmt, setup):
        self.stmt = stmt
        self.setup = setup

    def time(self):
        print('Total amount of time is', str(timeit(stmt=self.stmt, setup=self.setup)))
