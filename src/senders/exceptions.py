from fastapi import status

from src.exceptions import BadRequest, NotFound


class SenderNotFound(NotFound):
    detail = "Sender ID not found"


class SenderAlreadyExists(BadRequest):
    status_code = status.HTTP_409_CONFLICT
    detail = "This sender ID already exists on your account"


class InvalidSenderId(BadRequest):
    detail = "Invalid, unapproved or missing sender ID"
