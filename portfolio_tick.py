import helpers
import datetime as dt
import database 
from globals import *
import helpers 
import logger
from robin_stocks import robinhood as rh


class AccountTickData:
    def __init__(self, database, logger):
        self.database = database
        self.logger = logger
        self.types = [
            'text',
            'real',
            'real',
            'real',
            'real',
            'real',
            'real',
            'real',
            'text',
            'text',
            'text'
        ]
        self.cols = [
            "utc_datetime",
            'equity_previous_close',
            'equity',
            'extended_hours_equity',
            'market_value',
            'extended_hours_market_value',
            'buying_power',
            'withdrawable_amount',
            'equities',
            'crypto',
            'options'
        ]

        self.table_name = "account_info"
        self.database.create_table(self.table_name, self.cols, self.types)
        self.logger = logger

    def append_acc_data(self, check_market_hours=True):
        if check_market_hours:
            if not helpers.is_market_open():
                return

        try:
            portfolio_profile = rh.load_portfolio_profile()
            phx = rh.load_phoenix_account()
            equities = rh.build_holdings()
        except:
            self.logger.critical("COULD NOT PULL ACCOUNT INFO")
            return
        data = {}
        data["utc_datetime"] = f"{dt.datetime.utcnow()}"
        data["equity_previous_close"] = float(
            portfolio_profile["equity_previous_close"])
        data["equity"] = float(portfolio_profile["equity"])
        data["market_value"] = float(portfolio_profile["market_value"])
        try:
            data["extended_hours_equity"] = float(
                portfolio_profile["extended_hours_equity"])
            data["extended_hours_market_value"] = float(
                portfolio_profile["extended_hours_market_value"])
        except:
            data["extended_hours_equity"] = data["equity"]
            data["extended_hours_market_value"] = data["market_value"]
        data["withdrawable_amount"] = float(
            portfolio_profile["withdrawable_amount"])

        data["buying_power"] = float(phx["account_buying_power"]["amount"])
        data["equities"] = f"{equities}"
        data['crypto'] = f'{self.build_crypto()}'
        try:
            data['options'] = f'{rh.get_open_option_positions()}'
        except:
            data['options'] = 'ERR'
            self.logger.critical("FAILED TO PULL OPTION DATA")
        self.database.append_table(self.table_name, data)
        
        



    def build_crypto(self):
        try:
            crypto = rh.get_crypto_positions()
        except:
            self.logger.critical("COULD NOT PULL CRYPTO POSITIONS")
            return []
        
        data = []
        for ticker in crypto:
            if float(ticker["cost_bases"][0]["direct_quantity"]) > 0:
                temp = {}
                temp["ticker"] = ticker["currency"]["code"]
                temp['quantity'] = float(ticker["cost_bases"][0]["direct_quantity"])
                temp['cost_basis'] = float(ticker["cost_bases"][0]["direct_cost_basis"])
                temp['mark_price'] = float(rh.get_crypto_quote(temp["ticker"])['mark_price'])
                temp['equity'] = temp['mark_price']*temp['quantity']
                temp['profit_loss'] = temp['equity'] - temp['cost_basis']
                temp['pct_pl'] = temp['profit_loss'] / temp['cost_basis']
                data.append(temp)
        return data



def portfolio_tick_main():
    settings = globals.Globals()
    helpers.login(CREDS_PATH)
    log = logger.Logger().logger

    db = database.Database(DB_PATH, log)
    portfolio_db = AccountTickData(db, log)

    while True:
        portfolio_db.append_acc_data(CHECK_MARKET_HOURS)
        helpers.random_delay(DATA_COLLECT_FREQUENCY - 50, DATA_COLLECT_FREQUENCY+50)


if __name__ == "__main__":
    portfolio_tick_main()