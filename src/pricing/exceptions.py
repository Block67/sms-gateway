from src.exceptions import BadRequest


class PriceNotDefined(BadRequest):
    detail = "No price defined for this client/operator combination"
