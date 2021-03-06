from robin_stocks import robinhood as rh 
import datetime as dt
import numpy as np
import time
import json

def is_market_open(market="XNAS", extended=True):
    """
    returns bool
    """
    market_hours = rh.get_market_today_hours(market)
    if market_hours["opens_at"] is None:
        return False
    now = dt.datetime.utcnow()
    if extended:
        open = market_hours['extended_opens_at']
        close = market_hours['extended_closes_at']
        open = dt.datetime.strptime(open, '%Y-%m-%dT%H:%M:%SZ')
        close = dt.datetime.strptime(close, '%Y-%m-%dT%H:%M:%SZ')
    else:
        open = market_hours["opens_at"]
        close = market_hours["closes_at"]
        open = dt.datetime.strptime(open, '%Y-%m-%dT%H:%M:%SZ')
        close = dt.datetime.strptime(close, '%Y-%m-%dT%H:%M:%SZ')
    
    if now > open and now < close:
        return True
    else: 
        return False
        
def random_delay(min_time, max_time):
        """delays a random amount of time
        etween the min and max time in s."""
        time.sleep(np.random.randint(min_time, max_time))

def login(creds_filename="config.json"):
    # may need 2fa code entered throgh CLI
    content = open(creds_filename).read()
    config = json.loads(content)
    rh.login(config["username"], config["password"])

def get_option_expiration_dates(ticker):
    chains = rh.get_chains(ticker)
    expiration_dates = chains['expiration_dates']
    return expiration_dates



if __name__ == "__main__":
    pass 