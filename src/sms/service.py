from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.gateway.factory import get_gateway
from src.messages import service as message_service
from src.messages.constants import MessageStatus
from src.messages.models import Message
from src.operators import service as operator_service
from src.phone import service as phone_service
from src.pricing import service as pricing_service
from src.queue.publisher import publish_send_task
from src.senders import service as sender_service
from src.sms.exceptions import InsufficientBalance
from src.sms.schemas import SMSSendRequest
from src.users import service as user_service
from src.users.models import User

# Segments GSM 7-bit vs UCS-2, mêmes seuils que la libphonenumber/moment
# du projet Node original (160/153 caractères en simple/multi-segment GSM7).
GSM7_SINGLE_LIMIT = 160
GSM7_MULTI_LIMIT = 153
UCS2_SINGLE_LIMIT = 70
UCS2_MULTI_LIMIT = 67


def _count_pages(text: str) -> int:
    is_gsm7 = text.isascii()
    single_limit = GSM7_SINGLE_LIMIT if is_gsm7 else UCS2_SINGLE_LIMIT
    multi_limit = GSM7_MULTI_LIMIT if is_gsm7 else UCS2_MULTI_LIMIT

    if len(text) <= single_limit:
        return 1
    return -(-len(text) // multi_limit)  # ceil division


async def send_sms(db: AsyncSession, user: User, payload: SMSSendRequest) -> Message:
    sender_name = await sender_service.check_sender(db, user, payload.sender)
    phone = phone_service.parse_and_validate(payload.to)
    operator = await operator_service.resolve_operator(db, phone.e164)
    price = await pricing_service.get_price(db, user.id, operator.id)
    pages = _count_pages(payload.text)
    total_price = price * pages

    if total_price > (user.balance or Decimal(0)):
        raise InsufficientBalance

    message = await message_service.create_message(
        db,
        owner_id=user.id,
        sender_name=sender_name,
        to_number=phone.e164,
        text=payload.text,
        price=price,
        pages=pages,
        operator_id=operator.id,
        dlr_url=str(payload.dlr_url) if payload.dlr_url else None,
    )

    await user_service.debit_balance(db, user, total_price)

    try:
        await publish_send_task({"message_id": str(message.id)})
    except Exception:
        # La queue est indisponible : on retombe sur un envoi synchrone
        # immédiat plutôt que de perdre la requête (même filet de sécurité
        # que le fallback de SMSController.sendSms côté Node).
        gateway = get_gateway()
        result = await gateway.send(
            sender=sender_name, to=phone.e164, text=payload.text,
            dlr_url=str(payload.dlr_url) if payload.dlr_url else None,
        )
        status = MessageStatus.SENT if result.success else MessageStatus.REJECTED
        message = await message_service.update_status(
            db, message, status=status,
            provider_message_id=result.provider_message_id,
            error=None if result.success else result.description,
        )

    return message
