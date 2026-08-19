from fastapi import status

from src.exceptions import BadRequest


class InsufficientBalance(BadRequest):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    detail = "Insufficient balance to send this message"
