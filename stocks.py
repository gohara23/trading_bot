import helpers
import datetime as dt
import database 
from globals import *
import helpers 
import logger
from wallstreet import Stock


class StockTickData:

    def __init__(self, database, tickers, logger):
        self.database = database
        self.table_name = "stock_ticks"
        self.cols = [
            "utc_datetime", "symbol", "last_price", "last_trade_date"
        ]
        self.types = ['text', 'text', 'real', 'text'
                      ]
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

    def append_all_tickers(self, check_market_hours=True, extended_hours=False):
        if check_market_hours:
            if not helpers.is_market_open(extended=extended_hours):
                return
        for ticker in self.tickers:
            self.append_tick_data(ticker)

def stock_tick_main():
    log = logger.Logger().logger

    db = database.Database(DB_PATH, log)
    stocks_db = StockTickData(db, DATA_COLLECT_STOCKS, log)

    while True:
        stocks_db.append_all_tickers(CHECK_MARKET_HOURS, EXTENDED_HOURS_STOCKS)
        helpers.random_delay(DATA_COLLECT_FREQUENCY - 50, DATA_COLLECT_FREQUENCY+50)

if __name__ == "__main__":

    stock_tick_main()