import sqlite3
import pandas as pd

class DBHandler:
    def __init__(self):
        self.conn = sqlite3.connect('./dump/tastytrade.db')
        self.cursor = self.conn.cursor()

    def modify_table(self, table_name: str, jsonobject: dict, if_exists: str = 'fail', method: str = 'multi') -> None:
        df = pd.DataFrame(jsonobject)
        df.to_sql(name=table_name, con=self.conn, if_exists=if_exists, method=method)
