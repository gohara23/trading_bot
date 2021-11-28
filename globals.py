
class Globals():
    def __init__(self):
        self.TIME_FOR_EXECUTION = 45
        self.CREDS_PATH = r"config.json"
        self.DB_PATH = "database.db"
        self.DATA_COLLECT_STOCKS = ["TSLA", "AMD", "HUT", "AMC", "PLTR", "MARA", "GOEV", "RIOT", "BITO", "GME"]
        self.DATA_COLLECT_CRYPTO = ["BTC", "ETH", "DOGE"]
        self.DATA_COLLECT_FREQUENCY = 300 # seconds

        self.DATE_FORMAT = "%Y-%m-%d"
        self.CHECK_MARKET_HOURS = False


