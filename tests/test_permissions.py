"""Unit tests for the tenant token exchange without external network calls."""
import importlib.util
import io
import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "custom_components" / "ewe_go" / "permissions.py"
spec = importlib.util.spec_from_file_location("permissions_under_test", MODULE)
permissions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(permissions)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return io.BytesIO(json.dumps(self.payload).encode())

    def __exit__(self, *_):
        return False


class TestPermissions(TestCase):
    def test_exchange_request_and_response(self):
        def respond(request, timeout):
            self.assertEqual(request.get_method(), "POST")
            self.assertEqual(request.get_header("Identity"), "prod-ego-bax")
            self.assertEqual(request.get_header("Authorization"), "Bearer sample")
            self.assertEqual(json.loads(request.data), {"tenantId": "ego"})
            self.assertIn("version=v2", request.full_url)
            return FakeResponse({"token_type": "Bearer", "access_token": "other", "expires_in": 3600})
        with patch.object(permissions.urllib.request, "urlopen", respond):
            token, expiration = permissions._exchange("sample")
        self.assertEqual(token, "other")
        self.assertGreater(expiration, permissions.time.monotonic() + 3200)

    def test_missing_token(self):
        with patch.object(permissions.urllib.request, "urlopen", return_value=FakeResponse({"token_type": "Bearer", "expires_in": 3600})):
            with self.assertRaises(permissions.PermissionsError):
                permissions._exchange("sample")
