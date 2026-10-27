"""Constants for EWE Go."""
DOMAIN = "ewe_go"
API_URL = "https://app-backend.ewe-go.de/api"
CONF_ACCESS_TOKEN = "access_token"

# Confirmed from the EWE Go web login InitiateAuth request.
COGNITO_REGION = "eu-central-1"
COGNITO_APP_CLIENT_ID = "6eqi7k9jed2q0v8afbejv87qtu"
COGNITO_AUTH_FLOW = "USER_SRP_AUTH"
# User Pool ID must be identified before implementing SRP's password-claim proof.
