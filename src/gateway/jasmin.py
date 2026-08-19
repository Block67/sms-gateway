import base64

import httpx

from src.gateway.config import gateway_config
from src.gateway.schemas import GatewaySendResult


class JasminGateway:
    """Client HTTP vers l'API Jasmin (Basic Auth), équivalent Python de
    JasminService.ts (POST /secure/send, GET /rate, GET /secure/balance)."""

    def __init__(self) -> None:
        credentials = f"{gateway_config.JASMIN_USERNAME}:{gateway_config.JASMIN_PASSWORD}"
        token = base64.b64encode(credentials.encode()).decode()
        self._client = httpx.AsyncClient(
            base_url=gateway_config.JASMIN_BASE_URL,
            headers={"Authorization": f"Basic {token}"},
            timeout=15.0,
        )

    async def send(self, *, sender: str, to: str, text: str, dlr_url: str | None) -> GatewaySendResult:
        params: dict[str, str | int] = {"from": sender, "to": to, "content": text}
        if dlr_url:
            params.update({"dlr": "yes", "dlr-url": dlr_url, "dlr-level": 3, "dlr-method": "POST"})

        try:
            response = await self._client.get("/secure/send", params=params)
        except httpx.HTTPError as exc:
            return GatewaySendResult(success=False, provider_message_id=None, description=str(exc))

        if response.status_code != 200:
            return GatewaySendResult(success=False, provider_message_id=None, description=response.text)

        message_id = str(response.json().get("data", "")).replace('"', "")
        return GatewaySendResult(success=True, provider_message_id=message_id, description="Submitted")

    async def rate(self, *, to: str, text: str) -> float | None:
        try:
            response = await self._client.get("/rate", params={"to": to, "content": text})
            response.raise_for_status()
            unit_rate = response.json().get("unit_rate")
            return float(unit_rate) if unit_rate else None
        except httpx.HTTPError:
            return None

    async def balance(self) -> float | None:
        try:
            response = await self._client.get("/secure/balance")
            response.raise_for_status()
            balance = response.json().get("data", {}).get("balance")
            return float(balance) if balance is not None else None
        except httpx.HTTPError:
            return None
