import os

class Globals():
    def __init__(self):
        self.TIME_FOR_EXECUTION = 45
        self.CREDS_PATH = r"C:\Users\gabri\OneDrive - nd.edu\theta_bot\config.json"
        self.DB_PATH = "database.db"
        self.DATA_COLLECT_STOCKS = ["TSLA", "AMD", "HUT", "AMC", "PLTR", "MARA", "GOEV", "RIOT", "BITO", "GME"]
        self.DATA_COLLECT_CRYPTO = ["BTC", "ETH", "DOGE"]
        self.DATA_COLLECT_FREQUENCY = 300 # seconds
        # self.DB_PATH = os.getcwd()+"/db/"


if __name__ == "__main__":
    globals = Globals()
    print(globals.DB_PATH)

