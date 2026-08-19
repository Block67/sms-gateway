from src.exceptions import NotFound


class MessageNotFound(NotFound):
    detail = "Message not found"
