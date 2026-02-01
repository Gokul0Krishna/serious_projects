import sqlite3
from contextlib import contextmanager

class Dbconnect():
    def __init__(self):
        self.DB_PATH = 'C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Multi-Agent_Customer_Support_Automation\Database.db' 

    @contextmanager
    def get_db_connection(self):
        conn = sqlite3.connect(self.DB_PATH)
        try:
            conn.row_factory = sqlite3.Row   # safer dict-like access
            yield conn
            conn.commit()                    # commit only if no exception
        except Exception as e:
            conn.rollback()                  # rollback on error
            raise e
        finally:
            conn.close()