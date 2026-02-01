from base_aget import Dbconnect


class RefundPaymentAgent(Dbconnect):
    def __init__(self):
        super().__init__()
        self.REFUND_ESCALATION_THRESHOLD = 5000
        
    
    def _fetch_price(self, order_id: str):
        with self.get_db_connection() as conn:
            cursor = conn.execute(
                """
                SELECT *
                FROM payments
                WHERE order_id = ?
                """,
                (order_id)
            )
            return cursor.fetchone()
    
        def _view_payment(self, state, payment):
            state["context"]["payment"] = {
                "payment_id": payment.payment_id,
                "status": payment.status,
                "amount": payment.amount
            }
            return state

    def _view_payment(self, state, payment):
        state["context"]["payment"] = {
            "payment_id": payment.payment_id,
            "status": payment.status,
            "amount": payment.amount
        }
        return state
    
