from base_aget import Dbconnect
from typing import Dict, Any

class RefundPaymentAgent(Dbconnect):
    def __init__(self):
        super().__init__()
        self.REFUND_ESCALATION_THRESHOLD = 5000
        
    
    def _fetch_payment(self, order_id: str):
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
    
    def _error(self, state, message):
        state["error"] = message
        return state

    def _process_refund(self, state, db, payment, refund_amount: float):
        if payment.refund_status == "REFUNDED":
            return self._error(state, "Refund already processed")

        if refund_amount > payment.amount:
            return self._error(state, "Refund amount exceeds payment amount")

        success = self.gateway.initiate_refund(
            payment.payment_id,
            refund_amount
        )

        if not success:
            return self._error(state, "Refund initiation failed")

        payment.refund_status = "REFUNDED"
        db.commit()

        state["context"]["refund"] = {
            "payment_id": payment.payment_id,
            "amount": refund_amount,
            "status": "REFUNDED"
        }

        if refund_amount > self.REFUND_ESCALATION_THRESHOLD:
            state["context"]["escalate"] = True

        return state
    
    def run(self, state: Dict[str, Any]):
        state.setdefault("context", {})

        order_id = state.get("order_id")

        refund_amount = state.get("context", {}).get("ref   und_amount")

        if not order_id:
            return self._error(state, "Order ID is required for payment handling")

        payment = self._fetch_payment(order_id)

        if not payment:
            return self._error(state, "Payment record not found")

        if refund_amount:
            return self._process_refund(state, db, payment, refund_amount)

        return self._view_payment(state, payment)
