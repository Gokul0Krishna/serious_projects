import sqlite3
from contextlib import contextmanager

DB_PATH = r"C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Multi-Agent_Customer_Support_Automation\Database.db"


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.row_factory = sqlite3.Row   # safer dict-like access
        yield conn
        conn.commit()                    # commit only if no exception
    except Exception as e:
        conn.rollback()                  # rollback on error
        raise e
    finally:
        conn.close()


def _createordertable():
    with get_db_connection() as conn:
        conn.execute('''
                        CREATE TABLE IF NOT EXISTS orders (
                        order_id TEXT PRIMARY KEY,
                        customer_id UUID,
                        status TEXT,
                        eta TIMESTAMP,
                        amount FLOAT,
                        created_at TIMESTAMP
                        )
                    '''
                    )
        
def _createpaymenttable():
    with get_db_connection() as conn:
        conn.execute('''
                    CREATE TABLE IF NOT EXISTS payments (
                            payment_id TEXT PRIMARY KEY,
                            order_id TEXT,
                            status TEXT,
                            amount FLOAT,
                            refund_status TEXT,
                            created_at TIMESTAMP
                            )
                     ''')

if __name__ == '__main__':
    _createpaymenttable()