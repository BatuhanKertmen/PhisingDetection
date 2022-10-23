from python.Utilities.paths import WORKING_DIR
from datetime import datetime


class Log:
    def __init__(self):
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKCYAN = '\033[96m'
        self.OKGREEN = '\033[92m'
        self.FAIL = '\033[91m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'

    @staticmethod
    def log(message):
        dt = str(datetime.now())
        with open(str(WORKING_DIR) + "\\log.txt", "a") as file:
            file.write("log:\t" + dt + "\t" + str(message) + "\n")

    @staticmethod
    def warning(message):
        warning = '\033[93m'
        ends = '\033[0m'
        print(f"{warning}{message}{ends}")
        dt = str(datetime.now())
        with open(str(WORKING_DIR) + "\\log.txt", "a") as file:
            file.write("warn:\t" + dt + "\t" + str(message) + "\n")
        with open(str(WORKING_DIR) + "\\warnings.txt", "a") as file:
            file.write("warn:\t" + dt + "\t" + str(message) + "\n")

    @staticmethod
    def error(message):
        err = '\033[91m'
        ends = '\033[0m'
        print(f"{err}{message}{ends}")
        dt = str(datetime.now())
        with open(str(WORKING_DIR) + "\\log.txt", "a") as file:
            file.write("error:\t" + dt + "\t" + str(message) + "\n")
        with open(str(WORKING_DIR) + "\\warnings.txt", "a") as file:
            file.write("error:\t" + dt + "\t" + str(message) + "\n")
        with open(str(WORKING_DIR) + "\\errors.txt", "a") as file:
            file.write("error:\t" + dt + "\t" + str(message) + "\n")

    @staticmethod
    def success(message):
        suc = '\033[92m'
        ends = '\033[0m'
        print(f"{suc}{message}{ends}")
        dt = str(datetime.now())
        with open(str(WORKING_DIR) + "\\log.txt", "a") as file:
            file.write("succes:\t" + dt + "\t" + str(message) + "\n")