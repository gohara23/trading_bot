from robin_stocks import robinhood as rh
import sqlite3
import datetime as dt
import helpers


# add logger

class Database:

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, cols, types):
        """
        Creates a table if one of the same name does not 
        already exist 
        :type table_name: str
        :type cols: list str
        :type types: list str
        """
        if len(cols) != len(types):
            raise ValueError("number of columns must equal number of types")

        command = f"CREATE TABLE IF NOT EXISTS {table_name} ("

        for ix in range(len(cols)):
            command += f" {cols[ix]} {types[ix]},"

        command = command[:-1]
        command += ")"
        self.cursor.execute(command)
        self.conn.commit()

    def append_table(self, table_name, row):

        num_cols = self.get_num_cols(table_name)
        if len(row) != num_cols:
            raise ValueError("num input args does not match num cols")
        if type(row) is not dict:
            raise TypeError(
                f"Expected type of dict for arg row, but received {type(row)}")

        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        names = [description[0] for description in self.cursor.description]
        cmd = f"INSERT INTO {table_name} VALUES("
        for name in names:
            cmd += f":{name},"
        cmd = cmd[:-1]
        cmd += ")"
        self.cursor.execute(cmd, row)

        self.conn.commit()

    def get_num_cols(self, table_name):
        query = f"SELECT * FROM {table_name}"
        self.cursor.execute(query)
        names = [description[0] for description in self.cursor.description]
        num_cols = len(names)
        return num_cols


class StockTickData:

    def __init__(self, database, tickers):
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

    def add_ticker(self, ticker):
        self.tickers.append(ticker)

    def append_tick_data(self, ticker):
        # does not check if market is open
        quote = rh.get_stock_quote_by_symbol(ticker)
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
        db_input["pct_change_from_prev_close"] = (
            db_input["last_trade_price"]-db_input["previous_close"])/db_input["previous_close"]

        self.database.append_table(self.table_name, db_input)

    def append_all_tickers(self, check_market_hours=True, extended_hours=True):
        if not helpers.is_market_open(extended=extended_hours):
            return

        for ticker in self.tickers:
            self.append_tick_data(ticker)


class CryptoTickData:

    def __init__(self, database, tickers):
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

    def add_ticker(self, ticker):
        self.tickers.append(ticker)

    def append_tick_data(self, ticker):
        try:
            quote = rh.get_crypto_quote(ticker)
        except:
            # add logging here
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

    def append_all_tickers(self):
        for ticker in self.tickers:
            self.append_tick_data(ticker)

    class OptionTickData:
        def __init__(self, database, tickers):
            self.table_name = "options_tick_data"
            self.tickers = tickers
            self.database = database
            self.cols = [
                "utc_datetime",
                'adjusted_mark_price',
                'ask_price',
                'ask_size',
                'bid_price',
                'bid_size',
                'break_even_price',
                'chain_id',
                'chain_symbol',
                'chance_of_profit_long',
                'chance_of_profit_short',
                'created_at',
                'delta',
                'expiration_date',
                'gamma',
                'high_fill_rate_buy_price',
                'high_fill_rate_sell_price',
                'high_price',
                'implied_volatility',
                'issue_date',
                'last_trade_price',
                'last_trade_size',
                'low_fill_rate_buy_price',
                'low_fill_rate_sell_price',
                'low_price',
                'mark_price',
                'occ_symbol',
                'open_interest',
                'previous_close_date',
                'previous_close_price',
                'rho',
                'rhs_tradability',
                'sellout_datetime',
                'short_strategy_code',
                'state',
                'strike_price',
                'symbol',
                'theta',
                'tradability',
                'type',
                'updated_at',
                'vega',
                'volume'
            ]
            self.types = [ 
                "text",
                "real",
                "real",
                "real",
                "real",
                "real",
                "real",
                "text",
                "text",
                "real",
                "real",
                "text",
                "real",
                "text",
                "real",
                "real",
                "real",
                "real",
                "real",
                "text",
                "real",
                "real",
                "real",
                "real",
                "real",
                "real",
                "text",
                "real",
                "text",
                "real",
                "real",
                "text",
                "text",
                "text",
                "text",
                "real",
                "text",
                "real",
                "text",
                "text",
                "text",
                "real",
                "real",
            ]

            self.database.create_table(self.table_name, self.cols, self.types)

        def add_ticker(self, ticker):
            self.tickers.append(ticker)

        def append_tick_data(self, ticker, expiration):
            data = rh.find_options_by_expiration(ticker, expiration)
            final_dict = {}
            final_dict["utc_datetime"] = f"{dt.datetime.utcnow()}"
            for ix in range(1, len(self.cols)):
                if self.types[ix] == "text":
                    final_dict[self.cols[ix]] = f"{data[self.cols[ix]]}"
                elif self.types[ix] == "real":
                    final_dict[self.cols[ix]] = float(data[self.cols[ix]])
                else:
                    final_dict[self.cols[ix]] = data[self.cols[ix]]

            self.database.append_table(self.table_name, final_dict)

        def append_all(self):
            for ticker in self.tickers:
                expiris = helpers.get_option_expiration_dates(ticker)
                for expiri in expiris:
                    try:
                        self.append_tick_data(ticker, expiri)
                    except:
                        # Add logging!!
                        continue




if __name__ == "__main__":

    db = Database("test.db")
    name = "func_test"
    cols = ["datetime", "ticker", "price"]
    types = ["text", "text", "real"]
    db.create_table(name, cols, types)
    db.get_num_cols(name)
    inputs = ["05-21-2021", "TSLA", 1110]
    inputs = {"datetime": "05-21-2021", "ticker": "TSLA", "price": 420}
    db.append_table(name, inputs)

    # settings = globals.Globals()

    # conn = sqlite3.connect(settings.DB_PATH)

    # cursor = conn.cursor()
    # # cursor.execute("""CREATE TABLE employees (
    # #     first text,
    # #     last text,
    # #     pay integer
    # # )""")

    # # cursor.execute("INSERT INTO employees VALUES ('Gabriel', 'OHara', 20)")

    # cursor.execute("SELECT * FROM employees WHERE last='OHara'")

    # print(cursor.fetchall())

    # conn.commit()
    # conn.close()
