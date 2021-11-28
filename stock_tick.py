import helpers
import datetime as dt
import database 
import globals
import helpers 
import logger
from robin_stocks import robinhood as rh



class StockTickData:

    def __init__(self, database, tickers, logger):
        self.database = database
        self.table_name = "stock_tick_data"
        self.cols = [
            "utc_datetime", "symbol", "bid_price", "ask_price",
            "bid_size", "ask_size", "last_trade_price",
            "previous_close", "previous_close_date", "updated_at",
            "pct_change_from_prev_close"
        ]
        self.types = ['text', 'text', 'real', 'real',
                      'real', 'real', 'real',
                      'real', 'text', 'text',
                      'real'
                      ]
        self.database.create_table(self.table_name, self.cols, self.types)
        self.tickers = tickers
        self.logger = logger

    def add_ticker(self, ticker):
        self.tickers.append(ticker)

    def append_tick_data(self, ticker):
        # does not check if market is open
        try:
            quote = rh.get_stock_quote_by_symbol(ticker)
        except:
            self.logger.critical("STOCK QUOTE ERROR, TICKER SKIPPED")
            return

        db_input = {}
        db_input["utc_datetime"] = f"{dt.datetime.utcnow()}"
        db_input["symbol"] = ticker
        db_input["bid_price"] = float(quote["bid_price"])
        db_input["ask_price"] = float(quote["ask_price"])
        db_input["bid_size"] = float(quote["bid_size"])
        db_input["ask_size"] = float(quote["ask_size"])
        db_input["last_trade_price"] = float(quote["last_trade_price"])
        db_input["previous_close"] = float(quote["previous_close"])
        db_input["previous_close_date"] = quote["previous_close_date"]
        db_input["updated_at"] = quote["updated_at"]
        db_input["pct_change_from_prev_close"] = (
            db_input["last_trade_price"]-db_input["previous_close"])/db_input["previous_close"]

        self.database.append_table(self.table_name, db_input)

    def append_all_tickers(self, check_market_hours=True, extended_hours=True):
        if check_market_hours:
            if not helpers.is_market_open(extended=extended_hours):
                return

        for ticker in self.tickers:
            self.append_tick_data(ticker)

def stock_tick_main():
    settings = globals.Globals()
    helpers.login(settings.CREDS_PATH)
    log = logger.Logger().logger

    db = database.Database(settings.DB_PATH, log)
    stocks_db = StockTickData(db, settings.DATA_COLLECT_STOCKS, log)

    while True:
        stocks_db.append_all_tickers(settings.CHECK_MARKET_HOURS)
        helpers.random_delay(settings.DATA_COLLECT_FREQUENCY - 50, settings.DATA_COLLECT_FREQUENCY+50)

if __name__ == "__main__":

    stock_tick_main()