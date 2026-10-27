"""Exchange a Cognito token for an EWE Go tenant authorization token.

The endpoint and response fields were observed in the EWE Go web portal.
"""
from __future__ import annotations

import asyncio
import json
import time
import urllib.error
import urllib.request

PERMISSIONS_URL = "https://permissions.ewe-go.de/v1/auth/token?version=v2"
IDENTITY = "prod-ego-bax"
TENANT_ID = "ego"


class PermissionsError(Exception):
    """Permissions service failed without exposing credential material."""


class PermissionsUnauthorized(PermissionsError):
    """Cognito credential was rejected by permissions service."""


def _exchange(cognito_bearer: str) -> tuple[str, float]:
    request = urllib.request.Request(
        PERMISSIONS_URL,
        data=json.dumps({"tenantId": TENANT_ID}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {cognito_bearer}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Identity": IDENTITY,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise PermissionsUnauthorized(f"Permissions service rejected Cognito token (HTTP {exc.code})") from None
        raise PermissionsError(f"Permissions service returned HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise PermissionsError("Permissions request or response failed") from None
    if not isinstance(result, dict) or result.get("token_type", "").lower() != "bearer":
        raise PermissionsError("Permissions service returned an unexpected token type")
    token = result.get("access_token")
    ttl = result.get("expires_in")
    if not isinstance(token, str) or not token:
        raise PermissionsError("Permissions service returned no access token")
    try:
        ttl_seconds = float(ttl)
    except (TypeError, ValueError):
        raise PermissionsError("Permissions service returned invalid expiry") from None
    if ttl_seconds <= 0:
        raise PermissionsError("Permissions service returned an expired token")
    # Cache safely and renew before expiry; monotonic protects against clock changes.
    return token, time.monotonic() + max(0, ttl_seconds - min(300, ttl_seconds * 0.1))


async def exchange_token(cognito_bearer: str) -> tuple[str, float]:
    """Run blocking permissions exchange in a worker thread."""
    return await asyncio.to_thread(_exchange, cognito_bearer)
