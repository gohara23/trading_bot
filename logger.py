import logging 
import datetime as dt

class Logger:

    def __init__(self):
        today = dt.datetime.today()
        log_filename = f"{today.month:02d}-{today.day:02d}-{today.year}.log"
        self.logger = logging.getLogger("THETA")
        self.logger.setLevel(level=logging.DEBUG)
        self.file_handler = logging.FileHandler(log_filename)
        self.file_handler.setLevel(level=logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s: %(levelname)s - %(message)s")
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)
        self.logger.info("Logger Setup Successful")


if __name__ == "__main__":
    pass 

