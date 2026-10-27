"""Unofficial GraphQL transport for EWE Go.

Queries were reconstructed from APK field names; server compatibility is unverified.
"""
from __future__ import annotations
import asyncio
import time
import json
import urllib.error
import urllib.request
from .const import API_URL
from .auth import renew
from .permissions import exchange_token, PermissionsError, PermissionsUnauthorized

ACTIVE_QUERY = "query GetActiveChargingSession { getActiveSession { id status } }"
SESSION_QUERY = """query ChargingSession($id: ID!) {
 chargingSession(id: $id) { id status locationId evseId kwh soc chargingStart chargingEnd
 currentKwh currentKwhPrice currentPowerInKw chargingConfirmed stopConfirmed
 allowPluggedInConfirmation isEweGo }
}"""
HISTORY_QUERY = """query ChargingHistory($nextKey: String, $year: Int, $month: Int) {
 chargingHistory(nextKey: $nextKey, year: $year, month: $month) {
 nextKey cdrs { id startTime endTime totalEnergy totalEnergyCost totalCostInclVat
 location { cpoName address city postalCode } }
 }
}"""

class EweGoApiError(Exception):
    """API or schema error."""

class EweGoAuthenticationError(EweGoApiError):
    """Authentication failed."""

class EweGoClient:
    """Client with Cognito authentication and token renewal."""

    def __init__(self, token: str, *, email=None, tokens=None, update_tokens=None) -> None:
        # Legacy entries use their manually entered token; Cognito sessions exchange it.
        self._token = token
        self._email = email
        self._tokens = tokens
        self._update_tokens = update_tokens
        self._permissions_token = None
        self._permissions_expiration = 0
        self._token_lock = asyncio.Lock()

    async def _ensure_token(self):
        """Refresh Cognito and exchange the tenant token if required."""
        if self._tokens is None:
            return
        async with self._token_lock:
            try:
                new_tokens = await renew(self._email, self._tokens)
            except Exception as exc:
                raise EweGoAuthenticationError("Cognito token renewal failed") from exc
            if new_tokens != self._tokens:
                self._tokens = new_tokens
                self._permissions_token = None
                self._permissions_expiration = 0
                if self._update_tokens:
                    self._update_tokens(new_tokens)
            if self._permissions_token and time.monotonic() < self._permissions_expiration:
                return
            try:
                token, expiry = await exchange_token(self._tokens["id_token"])
            except PermissionsUnauthorized as exc:
                raise EweGoAuthenticationError(str(exc)) from exc
            except PermissionsError as exc:
                raise EweGoApiError(str(exc)) from exc
            self._permissions_token = token
            self._permissions_expiration = expiry
            self._token = token

    def _request(self, query: str, variables: dict | None = None) -> dict:
        payload = json.dumps({"query": query, "variables": variables or {}}).encode()
        request = urllib.request.Request(API_URL, data=payload, headers={
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json", "Accept": "application/json",
            "User-Agent": "homeassistant-ewe-go/0.1.0",
        }, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                raise EweGoAuthenticationError(f"EWE Go backend rejected the authorization token (HTTP {exc.code})") from exc
            raise EweGoApiError(f"HTTP status {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            raise EweGoApiError("EWE Go request failed") from exc
        if result.get("errors"):
            message = "; ".join(str(error.get("message", "GraphQL error")) for error in result["errors"])
            if any(word in message.lower() for word in ("unauthoriz", "unauthenticat", "forbidden", "jwt expired")):
                raise EweGoAuthenticationError(message)
            raise EweGoApiError(message)
        if not isinstance(result.get("data"), dict):
            raise EweGoApiError("Missing GraphQL data")
        return result["data"]

    async def execute(self, query: str, variables: dict | None = None) -> dict:
        await self._ensure_token()
        return await asyncio.to_thread(self._request, query, variables)

    async def active_session(self) -> dict | None:
        data = await self.execute(ACTIVE_QUERY)
        active = data.get("getActiveSession")
        if not isinstance(active, dict) or not active.get("id"):
            return None
        details = await self.execute(SESSION_QUERY, {"id": active["id"]})
        return details.get("chargingSession")

    async def charging_history(self, year: int, month: int) -> list[dict]:
        sessions, next_key, visited = [], None, set()
        for _ in range(30):
            data = await self.execute(HISTORY_QUERY, {"year": year, "month": month, "nextKey": next_key})
            history = data.get("chargingHistory") or {}
            sessions.extend(history.get("cdrs") or [])
            next_key = history.get("nextKey")
            if not next_key or next_key in visited:
                break
            visited.add(next_key)
        return sessions
