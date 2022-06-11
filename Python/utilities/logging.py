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
    def warning(message):
        WARNING = '\033[93m'
        ENDC = '\033[0m'
        print(f"{WARNING}{message}{ENDC}")

    @staticmethod
    def error(message):
        ERR = '\033[91m'
        ENDC = '\033[0m'
        print(f"{ERR}{message}{ENDC}")

    @staticmethod
    def succes(message):
        SUC = '\033[92m'
        ENDC = '\033[0m'
        print(f"{SUC}{message}{ENDC}")