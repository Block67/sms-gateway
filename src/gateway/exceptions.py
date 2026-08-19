from fastapi import status

from src.exceptions import DetailedHTTPException


class GatewayUnavailable(DetailedHTTPException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "SMS gateway unavailable, please try again later"
