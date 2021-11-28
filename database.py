from robin_stocks import robinhood as rh
import sqlite3
import datetime as dt
import helpers

class Database:

    def __init__(self, db_path, logger):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.logger = logger

    def create_table(self, table_name, cols, types):
        """
        Creates a table if one of the same name does not 
        already exist 
        :type table_name: str
        :type cols: list str
        :type types: list str
        """
        if len(cols) != len(types):
            # raise ValueError("number of columns must equal number of types")
            
            self.logger.critical(
                f"TABLE {table_name} NOT CREATED - VALUE ERROR: NUM COLS MUST EQUAL NUM TYPES")

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
            # raise ValueError("num input args does not match num cols")
            self.logger.critical(f"COULD NOT APPEND {table_name}, INPUT ARGS != NUM COLS")
            return
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
           

# if __name__ == "__main__":

#     db = Database("test.db")
#     name = "func_test"
#     cols = ["datetime", "ticker", "price"]
#     types = ["text", "text", "real"]
#     db.create_table(name, cols, types)
#     db.get_num_cols(name)
#     inputs = ["05-21-2021", "TSLA", 1110]
#     inputs = {"datetime": "05-21-2021", "ticker": "TSLA", "price": 420}
#     db.append_table(name, inputs)
