# EWE Go for Home Assistant

Experimental HACS integration, version 0.4.0.

Android authentication uses the Cognito user pool `eu-central-1_SkJskob5v` and Android app client `1mfb3lbc4hqu34pd3tf8lmibn`. GraphQL requests go directly to `https://app-backend.ewe-go.de/api` using the Cognito access token and `x-api-key` from the APK's Android resource `API_KEY`.

Install via HACS and restart Home Assistant. After upgrading from 0.3.x, remove the existing EWE Go config entry and add it again to obtain tokens for the Android app client and supply the API key. Never post API keys, user tokens or passwords in issue reports.

The web portal's permissions token is not used for the Android GraphQL API. Authentication and reconstructed GraphQL queries still need end-to-end live verification.

Not affiliated with EWE Go.
