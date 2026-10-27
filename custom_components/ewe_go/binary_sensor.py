"""Binary sensors: no guessed plugged-in state."""
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([EweGoCharging(hass.data[DOMAIN][entry.entry_id])])

class EweGoCharging(CoordinatorEntity, BinarySensorEntity):
    _attr_name = "EWE Go Lädt"
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING
    _attr_has_entity_name = True
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_charging"
        self._attr_device_info = {"identifiers": {(DOMAIN, coordinator.entry.entry_id)}, "name": "EWE Go", "manufacturer": "EWE Go"}
    @property
    def is_on(self):
        active = (self.coordinator.data or {}).get("active")
        if not active: return False
        # Existence of session is not sufficient to imply energy is flowing.
        try: return float(active.get("currentPowerInKw") or 0) > 0
        except (TypeError, ValueError): return None
