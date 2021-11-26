import database 
import globals
import helpers 
import logger


def data_collection_main():

    settings = globals.Globals()
    
    helpers.login(settings.CREDS_PATH)
    
    log = logger.Logger().logger

    db = database.Database(settings.DB_PATH, log)

    stocks = database.StockTickData(db, settings.DATA_COLLECT_STOCKS, log)

    crypto = database.CryptoTickData(db, settings.DATA_COLLECT_CRYPTO, log)

    options = database.OptionTickData(db, settings.DATA_COLLECT_STOCKS, log)

    account = database.AccountTickData(db, log)

    while True:

        stocks.append_all_tickers()
        crypto.append_all_tickers()
        options.append_all()
        account.append_acc_data()

        helpers.random_delay(settings.DATA_COLLECT_FREQUENCY - 50, settings.DATA_COLLECT_FREQUENCY+50)
        




if __name__ == "__main__":

    data_collection_main()