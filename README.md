# EWE Go for Home Assistant

Unofficial HACS integration for EWE Go (**experimental v0.2.0**).

## Authentication

The EWE Go web portal uses Amazon Cognito `USER_SRP_AUTH` with pool
`eu-central-1_SkJskob5v` and app client `6eqi7k9jed2q0v8afbejv87qtu`.
The login form accepts email and password. pycognito implements the SRP exchange;
Home Assistant persists **access, ID and refresh tokens, not the password**.
Expired tokens are renewed via the Cognito refresh token. If renewal fails, remove
and re-add the integration. MFA and additional Cognito challenges are not supported.

## Installation

Add `https://github.com/DrLippe/homeassistant-ewe-go` to HACS as a custom
integration repository, install, restart Home Assistant, and add **EWE Go**
under Devices & Services.

## Limitations

This version is **not yet live-tested** against EWE Go's GraphQL backend.
The backend is currently called with the Cognito *access token*. If its API
requires an *ID token* or other headers, requests will fail until validated.
GraphQL operation shape and field compatibility also remain unverified.

Charging sensors cover active session status, power, delivered energy,
latest charge, costs, location and current-month history (not lifetime total).
An `Eingesteckt` sensor remains withheld until the actual API state mapping
can be validated. Previous manual-bearer-token config entries are supported
until their token expires.

Never paste passwords, access tokens, ID tokens, or refresh tokens into
issues or diagnostic logs. This integration is not affiliated with EWE Go.
