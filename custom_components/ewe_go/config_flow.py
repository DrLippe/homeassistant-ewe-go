"""EWE Go setup: temporary manually supplied bearer token."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_ACCESS_TOKEN

class EweGoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            token = user_input[CONF_ACCESS_TOKEN].strip()
            if not token:
                return self.async_show_form(step_id="user", data_schema=vol.Schema({vol.Required(CONF_ACCESS_TOKEN): str}), errors={"base": "invalid_auth"})
            await self.async_set_unique_id("ewe_go_account")
            self._abort_if_unique_id_configured()
            # No API validation here: authentication protocol needs confirmation.
            return self.async_create_entry(title="EWE Go", data={CONF_ACCESS_TOKEN: token})
        return self.async_show_form(step_id="user", data_schema=vol.Schema({vol.Required(CONF_ACCESS_TOKEN): str}))
