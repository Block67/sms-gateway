from typing import Protocol

from src.gateway.schemas import GatewaySendResult


class SMSGateway(Protocol):
    """Interface commune : peu importe le vrai fournisseur (Jasmin, Kannel,
    un autre agrégateur), le reste de l'app ne dépend que de ces méthodes."""

    async def send(self, *, sender: str, to: str, text: str, dlr_url: str | None) -> GatewaySendResult: ...

    async def rate(self, *, to: str, text: str) -> float | None: ...

    async def balance(self) -> float | None: ...
