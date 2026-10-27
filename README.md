# EWE Go for Home Assistant

Unofficial, experimental integration for EWE Go. **Not yet validated against a real account.**

## Current capabilities

The integration offers Home Assistant entities for active charging status, current charging power (kW), session energy (kWh), most recent charging session, location, costs, and current-month history. GraphQL schema compatibility and field units must still be confirmed using real API responses. The charging binary sensor uses reported power rather than assuming every open session is currently charging.

Install as a custom HACS integration from `https://github.com/DrLippe/homeassistant-ewe-go`, restart Home Assistant, and add **EWE Go** in Devices & Services.

## Authentication status

The supplied EWE Go Android APK uses React Native with a Hermes v96 bundle. Its JavaScript bundle includes AWS Amplify Auth / Cognito-related modules and strings `USER_POOL_ID`, `USER_POOL_CLIENT_ID`, `USER_POOL_REGION`, `refreshToken`, and `userPoolWebClientId`. This **does not prove** whether the app uses username-password, SRP, Hosted UI / PKCE, or a customized login path. Those options need to be distinguished before implementing login.

The integration **currently accepts only an externally obtained bearer access token**. It does not ask for or retain account passwords. It cannot renew access tokens automatically. If the token expires, Home Assistant will require intervention. Never place tokens in issues or diagnostic logs.

## Known API assumptions to validate

The backend URL appears to be `https://app-backend.ewe-go.de/api`. Queries named `GetActiveChargingSession`, `ChargingSession`, and `ChargingHistory` and fields such as `currentPowerInKw`, `currentKwh`, `currentKwhPrice`, `status`, and `totalEnergy` were found in the APK. The exact query shapes in `api.py` are reconstructed; the backend might reject them until the original GraphQL documents are extracted.

Charging history is currently scoped to the ongoing calendar month, not an all-time total. Plugged-in status is intentionally **not** exposed without trustworthy evidence. There is no guarantee the repository-local icon is used as a brand icon in Home Assistant.

## Next development work

1. Extract original login invocation, Cognito user pool/app client metadata, and challenge handling from the Hermes bundle.
2. Implement and test the correct authentication flow and token refresh.
3. Obtain a privacy-sanitized EWE Go app network trace for authentication and GraphQL schema validation; do not publish credentials or bearer/refresh tokens.
4. Add integration tests from redacted response fixtures and make provider status mappings explicit.

This project is not affiliated with EWE Go.
