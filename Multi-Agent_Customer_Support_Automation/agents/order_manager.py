import sqlite3
from contextlib import contextmanager
from typing import Dict, Any

class Order_manger():
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

    def _fetch_order(self, order_id: str, user_id: str):
        with self.get_db_connection() as conn:
            cursor = conn.execute(
                """
                SELECT order_id, customer_id, status, amount
                FROM orders
                WHERE order_id = ? AND customer_id = ?
                """,
                (order_id, user_id)
            )
            return cursor.fetchone()   # sqlite3.Row or None
    
    def _view_order(self, state, order):
        state["context"]["order"] = {
            "order_id": order["order_id"],
            "status": order["status"],
            "amount": order["amount"]
        }
        return state
    
    def _cancel_order(self, state, order):
        if order["status"] not in ("PLACED", "CONFIRMED"):
            return self._error(state, "Order cannot be cancelled")

        with self.get_db_connection() as conn:
            conn.execute(
                """
                UPDATE orders
                SET status = ?
                WHERE order_id = ?
                """,
                ("CANCELLED", order["order_id"])
            )

        state["context"]["order"] = {
            "order_id": order["order_id"],
            "status": "CANCELLED"
        }
        return state
    
    def _error(self, state: Dict[str, Any], message: str):
        state["error"] = message
        return state

    def run(self, state: Dict[str, Any]):
        state.setdefault("context", {})

        user_id = state.get("user_id")
        order_id = state.get("order_id")

        if not user_id or not order_id:
            return self._error(state, "User ID and Order ID are required")

        order = self._fetch_order(order_id, user_id)
        if not order:
            return self._error(state, "Order not found")

        action = str(state.get("message", "")).lower()

        if action == "view":
            return self._view_order(state, order)

        if action == "cancel":
            return self._cancel_order(state, order)

