from wallstreet import Stock, Call, Put
from pprint import pprint
from robin_stocks import robinhood as rh

from scipy.interpolate import interp1d
from scipy import sqrt, log, exp
from scipy.stats import norm
from scipy.optimize import fsolve

import datetime as dt
import database 
import globals
import helpers 
import logger


DELTA_DIFFERENTIAL = 1.e-3
VEGA_DIFFERENTIAL = 1.e-4
GAMMA_DIFFERENTIAL = 1.e-3
RHO_DIFFERENTIAL = 1.e-4
THETA_DIFFERENTIAL = 1.e-5

IMPLIED_VOLATILITY_TOLERANCE = 1.e-6
SOLVER_STARTING_VALUE = 0.27

OVERNIGHT_RATE = 0
RISK_FREE_RATE = 0.015


class BlackandScholes:

    def __init__(self, S, K, T, price, r, option, q=0):
        self.S, self.K, self.T, self.option, self.q = S, K, T, option, q
        self.r = r
        self.opt_price = price
        self.impvol = self.implied_volatility()
        self.vega_val = self.vega()
        self.delta_val = self.delta()
        self.gamma_val = self.gamma()
        self.rho_val = self.rho()
        self.theta_val = self.theta()

    @staticmethod
    def _BlackScholesCall(S, K, T, sigma, r, q):
        d1 = (log(S/K) + (r - q + (sigma**2)/2)*T)/(sigma*sqrt(T))
        d2 = d1 - sigma*sqrt(T)
        return S*exp(-q*T)*norm.cdf(d1) - K*exp(-r*T)*norm.cdf(d2)

    @staticmethod
    def _BlackScholesPut(S, K, T, sigma, r, q):
        d1 = (log(S/K) + (r - q + (sigma**2)/2)*T)/(sigma*sqrt(T))
        d2 = d1 - sigma*sqrt(T)
        return K*exp(-r*T)*norm.cdf(-d2) - S*exp(-q*T)*norm.cdf(-d1)

    def _fprime(self, sigma):
        logSoverK = log(self.S/self.K)
        n12 = ((self.r + sigma**2/2)*self.T)
        numerd1 = logSoverK + n12
        d1 = numerd1/(sigma*sqrt(self.T))
        return self.S*sqrt(self.T)*norm.pdf(d1)*exp(-self.r*self.T)

    def BS(self, S, K, T, sigma, r, q):
        if self.option == 'Call':
            return self._BlackScholesCall(S, K, T, sigma, r, q)
        elif self.option == 'Put':
            return self._BlackScholesPut(S, K, T, sigma, r, q)

    def implied_volatility(self):
        def impvol(x): return self.BS(self.S, self.K, self.T,
                                      x, self.r, self.q) - self.opt_price
        iv = fsolve(impvol, SOLVER_STARTING_VALUE,
                    fprime=self._fprime, xtol=IMPLIED_VOLATILITY_TOLERANCE)
        return iv[0]

    def delta(self):
        h = DELTA_DIFFERENTIAL
        p1 = self.BS(self.S + h, self.K, self.T, self.impvol, self.r, self.q)
        p2 = self.BS(self.S - h, self.K, self.T, self.impvol, self.r, self.q)
        return (p1-p2)/(2*h)

    def gamma(self):
        h = GAMMA_DIFFERENTIAL
        p1 = self.BS(self.S + h, self.K, self.T, self.impvol, self.r, self.q)
        p2 = self.BS(self.S, self.K, self.T, self.impvol, self.r, self.q)
        p3 = self.BS(self.S - h, self.K, self.T, self.impvol, self.r, self.q)
        return (p1 - 2*p2 + p3)/(h**2)

    def vega(self):
        h = VEGA_DIFFERENTIAL
        p1 = self.BS(self.S, self.K, self.T, self.impvol + h, self.r, self.q)
        p2 = self.BS(self.S, self.K, self.T, self.impvol - h, self.r, self.q)
        return (p1-p2)/(2*h*100)

    def theta(self):
        h = THETA_DIFFERENTIAL
        p1 = self.BS(self.S, self.K, self.T + h, self.impvol, self.r, self.q)
        p2 = self.BS(self.S, self.K, self.T - h, self.impvol, self.r, self.q)
        return (p1-p2)/(2*h*365)

    def rho(self):
        h = RHO_DIFFERENTIAL
        p1 = self.BS(self.S, self.K, self.T, self.impvol, self.r + h, self.q)
        p2 = self.BS(self.S, self.K, self.T, self.impvol, self.r - h, self.q)
        return (p1-p2)/(2*h*100)


def get_option_expiration_dates(ticker):
    chains = rh.get_chains(ticker)
    expiration_dates = chains['expiration_dates']
    return expiration_dates


def yrs_until_date_expiri(date):
    """
    :type :date: datetime object
    """
    now = dt.datetime.today()
    date += dt.timedelta(hours=16)
    now = dt.datetime.now()
    delta_t = date - now
    SECONDS_PER_DAY = 86400
    delta_t += dt.timedelta(1, 43200)
    T = (delta_t.days + (delta_t.seconds/SECONDS_PER_DAY)) / 365
    return T


def datetime_to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day


class OptionTickData:
    def __init__(self, database, tickers, logger):
        self.table_name = "options_tick_data"
        self.tickers = tickers
        self.database = database
        self.cols = [
            'ask',
            'bid',
            'change',
            'contractSymbol',
            'delta',
            'expiration',
            'gamma',
            'impliedVolatility',
            'inTheMoney',
            'lastPrice',
            'openInterest',
            'percentChange',
            'rho',
            'strike',
            'theta',
            'type',
            'utc_datetime',
            'vega',
            'volume',
            'underlying'
        ]
        self.types = [
            "real",
            'real',
            'real',
            'text',
            'real',
            'text',
            'real',
            'real',
            'text',
            'real',
            'real',
            'real',
            'real',
            'real',
            'real',
            'text',
            'text',
            'real',
            'real',
            'real'
        ]
        self.settings = globals.Globals()
        self.database.create_table(self.table_name, self.cols, self.types)
        self.logger = logger

    def add_ticker(self, ticker):
        self.tickers.append(ticker)

    def append_tick_data(self, ticker, expiration):
        date_obj = dt.datetime.strptime(expiration, self.settings.DATE_FORMAT)
        for type in ["Call", "Put"]:
            if type == "Call":
                chain = Call(ticker, date_obj.day,
                             date_obj.month, date_obj.year)
            else: 
                chain = Put(ticker, date_obj.day,
                             date_obj.month, date_obj.year)
            S = chain.underlying.price
            expiri_obj = dt.datetime.strptime(chain.expiration, '%d-%m-%Y')
            T = yrs_until_date_expiri(expiri_obj)
            expiri_str = dt.datetime.strftime(expiri_obj, self.settings.DATE_FORMAT)

            for option in chain.data:
                del option["contractSize"]
                del option["currency"]
                del option["lastTradeDate"]
                option['type'] = type
                option["utc_datetime"] = f"{dt.datetime.utcnow()}"
                option["expiration"] = expiri_str
                option["underlying"] = S
                K = option["strike"]
                option["inTheMoney"] = f"{option['inTheMoney']}"
                price = option['lastPrice']
                bs = BlackandScholes(S, K, T, price, RISK_FREE_RATE, type)
                option['delta'] = bs.delta_val
                option['gamma'] = bs.gamma_val
                option['theta'] = bs.theta_val
                option['rho'] = bs.rho_val
                option['vega'] = bs.vega_val

                self.database.append_table(self.table_name, option)

    def append_all(self, check_market_hours=True):
        if check_market_hours:
            if not helpers.is_market_open(extended=True):
                return

        for ticker in self.tickers:
            try:
                expiris = helpers.get_option_expiration_dates(ticker)
            except:
                self.logger.critical(
                    "COULD NOT FIND EXPIRIS, TICKER SKIPPED")
                continue
            for expiri in expiris:
                self.append_tick_data(ticker, expiri)
                try:
                    self.append_tick_data(ticker, expiri)
                except:
                    self.logger.critical(
                        "COULD NOT FIND OPTION DATA TICKER/EXPIRI SKIPPED")
                    continue


def options_collection_main():
    settings = globals.Globals()
    helpers.login(settings.CREDS_PATH)
    log = logger.Logger().logger

    db = database.Database(settings.DB_PATH, log)
    options_db = OptionTickData(db, settings.DATA_COLLECT_STOCKS, log)

    while True:
        options_db.append_all(settings.CHECK_MARKET_HOURS)
        helpers.random_delay(settings.DATA_COLLECT_FREQUENCY - 50, settings.DATA_COLLECT_FREQUENCY+50)


if __name__ == "__main__":
    options_collection_main()
