from fastapi import HTTPException, status


class DetailedHTTPException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Server error"

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("detail", self.detail)
        super().__init__(status_code=self.status_code, **kwargs)


class PermissionDenied(DetailedHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Permission denied"


class NotAuthenticated(DetailedHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Not authenticated"


class NotFound(DetailedHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Not found"


class BadRequest(DetailedHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad request"
