"""EWE Go sensors; unknown fields remain unavailable."""
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

DESCRIPTIONS = (
    SensorEntityDescription(key="status", name="Ladestatus", icon="mdi:ev-station"),
    SensorEntityDescription(key="power", name="Ladeleistung", native_unit_of_measurement=UnitOfPower.KILO_WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT),
    SensorEntityDescription(key="energy", name="Geladene Energie", native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING),
    SensorEntityDescription(key="location", name="Ladeort", icon="mdi:map-marker"),
    SensorEntityDescription(key="last_charge", name="Letzter Ladevorgang", device_class=SensorDeviceClass.TIMESTAMP),
    SensorEntityDescription(key="last_energy", name="Energie letzter Ladevorgang", native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY),
    SensorEntityDescription(key="last_cost", name="Kosten letzter Ladevorgang", native_unit_of_measurement="EUR", device_class=SensorDeviceClass.MONETARY),
    SensorEntityDescription(key="monthly_energy", name="Ladeenergie laufender Monat", native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY),
)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(EweGoSensor(coordinator, description) for description in DESCRIPTIONS)

class EweGoSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    def __init__(self, coordinator, description):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{description.key}"
        self._attr_device_info = {"identifiers": {(DOMAIN, coordinator.entry.entry_id)}, "name": "EWE Go", "manufacturer": "EWE Go"}

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        active, latest, history = data.get("active") or {}, data.get("latest") or {}, data.get("history") or []
        key = self.entity_description.key
        if key == "status": return active.get("status")
        if key == "power": return active.get("currentPowerInKw")
        if key == "energy": return active.get("currentKwh")
        if key == "location":
            location = latest.get("location") or {}
            return ", ".join(str(p) for p in (location.get("cpoName"), location.get("address"), location.get("city")) if p) or active.get("locationId")
        if key == "last_charge":
            from homeassistant.util import dt as dt_util
            value = latest.get("startTime")
            return dt_util.parse_datetime(value) if value else None
        if key == "last_energy": return latest.get("totalEnergy")
        if key == "last_cost": return latest.get("totalCostInclVat")
        if key == "monthly_energy":
            try: return sum(float(s["totalEnergy"]) for s in history if s.get("totalEnergy") is not None)
            except (ValueError, TypeError): return None
        return None
