from Python.utilities.paths import WORKING_DIR
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
        WARNING = '\033[93m'
        ENDC = '\033[0m'
        print(f"{WARNING}{message}{ENDC}")
        dt = str(datetime.now())
        with open(str(WORKING_DIR) + "\\log.txt", "a") as file:
            file.write("warn:\t" + dt + "\t" + str(message) + "\n")
        with open(str(WORKING_DIR) + "\\warnings.txt", "a") as file:
            file.write("warn:\t" + dt + "\t" + str(message) + "\n")

    @staticmethod
    def error(message):
        ERR = '\033[91m'
        ENDC = '\033[0m'
        print(f"{ERR}{message}{ENDC}")
        dt = str(datetime.now())
        with open(str(WORKING_DIR) + "\\log.txt", "a") as file:
            file.write("error:\t" + dt + "\t" + str(message) + "\n")
        with open(str(WORKING_DIR) + "\\warnings.txt", "a") as file:
            file.write("error:\t" + dt + "\t" + str(message) + "\n")
        with open(str(WORKING_DIR) + "\\errors.txt", "a") as file:
            file.write("error:\t" + dt + "\t" + str(message) + "\n")

    @staticmethod
    def succes(message):
        SUC = '\033[92m'
        ENDC = '\033[0m'
        print(f"{SUC}{message}{ENDC}")
        dt = str(datetime.now())
        with open(str(WORKING_DIR) + "\\log.txt", "a") as file:
            file.write("succes:\t" + dt + "\t" + str(message) + "\n")