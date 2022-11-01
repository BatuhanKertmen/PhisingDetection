from timeit import default_timer as timer


class Benchmark:
    def __init__(self, file=""):
        self._start = -1
        self._end = -1
        self._records = list()
        self._file = file

    def initializeTimer(self):
        self._start = timer()

    def record(self, message):
        if self._start == -1:
            raise RuntimeError("Object is not initialized!")

        self._records.append({"message": message, "elapsed time": timer() - self._start})

    def getRecords(self):
        if self._start == -1:
            return {}

        return {
            "elapsed_time": timer() - self._start,
            "records": self._records
        }

    def __del__(self, sa):
        if self._start == -1:
            return

        with open(self._file, "w") as file:
            file.write(str(self.getRecords()))
