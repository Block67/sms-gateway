import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.operators.exceptions import OperatorAlreadyExists, OperatorNotFound
from src.operators.models import Operator
from src.operators.schemas import OperatorCreate

MAX_PREFIX_LENGTH = 8


async def resolve_operator(db: AsyncSession, e164_number: str) -> Operator:
    """Résout l'opérateur par correspondance de préfixe le plus long,
    en une seule requête indexée (IN + ORDER BY length DESC LIMIT 1)."""
    digits = e164_number.lstrip("+")
    candidates = [digits[:length] for length in range(1, min(len(digits), MAX_PREFIX_LENGTH) + 1)]

    result = await db.execute(
        select(Operator)
        .where(Operator.prefix.in_(candidates))
        .order_by(func.length(Operator.prefix).desc())
        .limit(1)
    )
    operator = result.scalar_one_or_none()
    if operator is None:
        raise OperatorNotFound
    return operator


async def list_operators(db: AsyncSession) -> list[Operator]:
    result = await db.execute(select(Operator).order_by(Operator.prefix))
    return list(result.scalars().all())


async def create_operator(db: AsyncSession, payload: OperatorCreate) -> Operator:
    operator = Operator(**payload.model_dump())
    db.add(operator)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise OperatorAlreadyExists from exc
    await db.refresh(operator)
    return operator


async def get_operator_or_404(db: AsyncSession, operator_id: uuid.UUID) -> Operator:
    operator = await db.get(Operator, operator_id)
    if operator is None:
        raise OperatorNotFound
    return operator
