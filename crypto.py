import helpers
import datetime as dt
import database
import globals
import helpers
import logger
from wallstreet import Stock


class CryptoTick:

    def __init__(self, database, tickers, logger):
        self.database = database
        self.table_name = "crypto"
        self.cols = [
            "utc_datetime", "symbol", "last_price", "last_trade_date"
        ]
        self.types = ['text', 'text', 'real', 'text']
        self.database.create_table(self.table_name, self.cols, self.types)
        self.tickers = tickers
        self.logger = logger

    def add_ticker(self, ticker):
        self.tickers.append(ticker)

    def append_tick_data(self, ticker):
        # does not check if market is open
        try:
            quote = Stock(ticker)
        except:
            self.logger.critical("STOCK QUOTE ERROR, TICKER SKIPPED")
            return

        db_input = {}
        db_input["utc_datetime"] = f"{dt.datetime.utcnow()}"
        db_input["symbol"] = ticker
        db_input["last_price"] = quote.price
        db_input["last_trade_date"] = quote.last_trade

        self.database.append_table(self.table_name, db_input)

    def append_all_tickers(self):
        for ticker in self.tickers:
            self.append_tick_data(ticker)


def crypto_main():
    settings = globals.Globals()
    log = logger.Logger().logger

    db = database.Database(settings.DB_PATH, log)
    stocks_db = CryptoTick(db, settings.CRYPTO_PAIRS, log)

    while True:
        stocks_db.append_all_tickers()
        helpers.random_delay(settings.DATA_COLLECT_FREQUENCY -
                             50, settings.DATA_COLLECT_FREQUENCY+50)


if __name__ == "__main__":

    crypto_main()
