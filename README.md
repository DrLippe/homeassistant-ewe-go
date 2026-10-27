# EWE Go for Home Assistant

Unofficial experimental HACS integration, version **0.3.0**.

## Authentication

1. Sign in to Amazon Cognito using email/password and `USER_SRP_AUTH`
   (pool `eu-central-1_SkJskob5v`, web client `6eqi7k9jed2q0v8afbejv87qtu`).
2. Exchange a Cognito bearer at
   `POST https://permissions.ewe-go.de/v1/auth/token?version=v2`,
   with header `identity: prod-ego-bax` and JSON body `{"tenantId":"ego"}`.
3. Cache the resulting `access_token` until shortly before its
   `expires_in` expiration, then renew it as needed.
4. Use the exchanged bearer for GraphQL calls to
   `https://app-backend.ewe-go.de/api` (**still to be verified**).

The implementation currently sends the Cognito **ID token** to the
permissions service. The captured request had a redacted Authorization
header, so whether this endpoint expects the Cognito ID token or
access token remains **unverified**. Likewise, the Android app may
use a different application client or API authentication flow.
The code does not persist the user's password; it stores Cognito
tokens in the Home Assistant config entry. The tenant bearer token
is cached only in memory.

**Experimental: no successful end-to-end test has been performed.**
Do not publish authentication tokens or cookies in bug reports.

## Installation

Add `https://github.com/DrLippe/homeassistant-ewe-go` to HACS as
a custom integration repository, install, restart Home Assistant,
then add **EWE Go** under Devices & Services.

## Sensors

Active charging status, current charging power, session energy,
last charging record, location, costs, and the current month's
charging history are mapped from reconstructed APK GraphQL query
shapes. Backend schema and token authorization remain unverified.
The plugged-in binary sensor is intentionally not guessed.
Manual token entries from 0.1.x remain supported until token expiry.

## Troubleshooting

When setup fails, inspect Home Assistant's logs for the stage:
- `Cognito token renewal failed`: Cognito token stage.
- `Permissions service rejected Cognito token (HTTP 401/403)`: tenant exchange; verify the Cognito token type.
- `EWE Go backend rejected the authorization token (HTTP 401/403)`: GraphQL backend token not accepted.
- `GraphQL error`: verify query shape and backend schema.

The source includes isolated tests for the permissions exchange:
`python -m unittest discover -s tests -v`.

This project is not affiliated with EWE Go.
