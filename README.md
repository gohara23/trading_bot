# trading_bot
Python algorithmic trading bot using the Robinhood API and an SQLite database


## globals.py

For set up, you must specify the path for a file containing your Robinhood credentials.


```json
    self.CREDS_PATH = r"YOUR_FILE_PATH"
  ```

The json file should be structured as follows:

```json
  {
    "username": "email@email.com",
    "password": "password123"
  }
  ```