import phonenumbers
from phonenumbers import NumberParseException

from src.phone.exceptions import InvalidPhoneNumber
from src.phone.schemas import PhoneInfo


def parse_and_validate(raw_number: str) -> PhoneInfo:
    try:
        parsed = phonenumbers.parse(raw_number, None)
    except NumberParseException as exc:
        raise InvalidPhoneNumber from exc

    if not phonenumbers.is_valid_number(parsed):
        raise InvalidPhoneNumber

    e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

    return PhoneInfo(
        e164=e164,
        country_code=phonenumbers.region_code_for_number(parsed),
        calling_code=parsed.country_code,
    )
