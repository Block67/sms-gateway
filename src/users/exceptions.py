from fastapi import status

from src.exceptions import DetailedHTTPException


class InvalidApiKey(DetailedHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid or missing API key"
