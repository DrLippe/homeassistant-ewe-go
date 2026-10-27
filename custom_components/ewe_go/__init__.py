"""EWE Go Home Assistant integration."""
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .api import EweGoClient
from .const import DOMAIN, CONF_EMAIL, CONF_ACCESS_TOKEN, CONF_ID_TOKEN, CONF_REFRESH_TOKEN, CONF_API_KEY
from .coordinator import EweGoCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if CONF_EMAIL in entry.data:
        tokens = {k: entry.data[k] for k in (CONF_ACCESS_TOKEN, CONF_ID_TOKEN, CONF_REFRESH_TOKEN)}
        def save_tokens(new_tokens):
            hass.config_entries.async_update_entry(entry, data={**entry.data, **new_tokens})
        client = EweGoClient(entry.data[CONF_ACCESS_TOKEN], email=entry.data[CONF_EMAIL], tokens=tokens, update_tokens=save_tokens, api_key=entry.data.get(CONF_API_KEY))
    else:
        client = EweGoClient(entry.data[CONF_ACCESS_TOKEN], api_key=entry.data.get(CONF_API_KEY))
    coordinator = EweGoCoordinator(hass, client, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok
