import uuid

from src.gateway.schemas import GatewaySendResult


class LocalGateway:
    """Gateway simulée pour le développement/les tests, sans dépendance
    externe : renvoie toujours un succès immédiat (aucun SMS réel envoyé)."""

    async def send(self, *, sender: str, to: str, text: str, dlr_url: str | None) -> GatewaySendResult:
        return GatewaySendResult(
            success=True, provider_message_id=str(uuid.uuid4()), description="Simulated (local gateway)"
        )

    async def rate(self, *, to: str, text: str) -> float | None:
        return None

    async def balance(self) -> float | None:
        return None
