from src.exceptions import BadRequest


class InvalidPhoneNumber(BadRequest):
    detail = "Invalid phone number, use E.164 format (e.g. +22997123456)"
