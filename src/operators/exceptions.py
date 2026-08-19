from src.exceptions import BadRequest, NotFound


class OperatorNotFound(NotFound):
    detail = "No operator matches this phone number"


class OperatorAlreadyExists(BadRequest):
    detail = "An operator with this prefix already exists"
