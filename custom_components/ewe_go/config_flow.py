"""Configure EWE Go using Cognito USER_SRP_AUTH."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from .auth import login
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class EweGoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            email = user_input[CONF_EMAIL].strip().lower()
            try:
                tokens = await login(email, user_input[CONF_PASSWORD])
            except Exception:
                _LOGGER.warning("EWE Go login failed")
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(email)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=email, data={CONF_EMAIL: email, **tokens})
        return self.async_show_form(step_id="user", data_schema=vol.Schema({
            vol.Required(CONF_EMAIL, default=(user_input or {}).get(CONF_EMAIL, "")): str,
            vol.Required(CONF_PASSWORD): str,
        }), errors=errors)
