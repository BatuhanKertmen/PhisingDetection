import json
from timeit import default_timer as timer


class Benchmark:
    def __init__(self):
        self._start = -1
        self._end = -1
        self._records = list()

    def initializeTimer(self):
        self._start = float("{:.2f}".format(timer()))

    def record(self, message):
        if self._start == -1:
            raise RuntimeError("Object is not initialized!")

        formatted_elapsed_time = "{:.2f}".format(timer() - self._start)
        self._records.append({"message": message, "elapsed time": formatted_elapsed_time})

    def getRecords(self):
        if self._start == -1:
            return {}

        return {
            "elapsed_time": "{:.2f}".format(timer() - self._start),
            "records": self._records
        }

    def reset(self):
        self._start = float("{:.2f}".format(timer()))
        self._end = -1
        self._records = list()

    def writeRecords(self, file):
        if self._start == -1:
            return

        with open(file, "w") as file:
            json.dump(self.getRecords(), file)
