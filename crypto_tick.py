import helpers
import datetime as dt
import database
from globals import *
import helpers
import logger
from robin_stocks import robinhood as rh


class CryptoTickData:

    def __init__(self, database, tickers, logger):
        self.table_name = "crypto_tick_data"
        self.database = database
        self.tickers = tickers
        self.cols = [
            "utc_datetime", "symbol", "bid_price", "ask_price", "mark_price",
            "high_price", "low_price", "open_price"
        ]
        self.types = [
            "text", "text", "real", "real", "real",
                    "real", "real", "real"
        ]
        self.database.create_table(self.table_name, self.cols, self.types)
        self.logger = logger

    def add_ticker(self, ticker):
        self.tickers.append(ticker)

    def append_tick_data(self, ticker):
        try:
            quote = rh.get_crypto_quote(ticker)
        except:
            self.logger.critical("CRYPTO QUOTE ERROR, TICKER SKIPPED")
            return
        db_input = {}
        db_input["utc_datetime"] = f"{dt.datetime.utcnow()}"
        db_input["symbol"] = ticker
        db_input["bid_price"] = float(quote["bid_price"])
        db_input["ask_price"] = float(quote["ask_price"])
        db_input["mark_price"] = float(quote["mark_price"])
        db_input["high_price"] = float(quote["high_price"])
        db_input["low_price"] = float(quote["low_price"])
        db_input["open_price"] = float(quote["open_price"])

        self.database.append_table(self.table_name, db_input)

    def append_all_tickers(self):
        for ticker in self.tickers:
            self.append_tick_data(ticker)


def crypto_tick_main():
    helpers.login(CREDS_PATH)
    log = logger.Logger().logger

    db = database.Database(DB_PATH, log)
    crypto_db = CryptoTickData(db, DATA_COLLECT_CRYPTO, log)

    while True:
        crypto_db.append_all_tickers()
        helpers.random_delay(DATA_COLLECT_FREQUENCY -
                             50, DATA_COLLECT_FREQUENCY+50)


if __name__ == "__main__":
    crypto_tick_main()
