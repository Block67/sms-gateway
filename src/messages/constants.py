from enum import StrEnum


class MessageStatus(StrEnum):
    QUEUED = "queued"
    SUBMITTED = "submitted"
    SENT = "sent"
    DELIVERED = "delivered"
    UNDELIVERED = "undelivered"
    REJECTED = "rejected"
    PROGRAMMED = "programmed"
