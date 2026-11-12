"""Polling for EWE Go."""
import logging
from datetime import datetime, timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed
from .api import EweGoApiError, EweGoAuthenticationError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

ACTIVE_POLL_INTERVAL = timedelta(seconds=30)
IDLE_POLL_INTERVAL = timedelta(minutes=5)

class EweGoCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, client, entry):
        super().__init__(hass, logger=_LOGGER, name=DOMAIN,
                         update_interval=IDLE_POLL_INTERVAL)
        self.client, self.entry = client, entry
        self._history = []
        self._history_month = None

    async def _async_update_data(self):
        try:
            active = await self.client.active_session()
            # DataUpdateCoordinator schedules the next refresh using this interval.
            # An active session gets faster updates; otherwise reduce API traffic.
            self.update_interval = ACTIVE_POLL_INTERVAL if active else IDLE_POLL_INTERVAL
            now = datetime.now()
            month = (now.year, now.month)
            # Refresh history hourly, or on first load or session completion.
            refresh = (self._history_month != month or not hasattr(self, "_history_fetched")
                       or now - self._history_fetched >= timedelta(hours=1)
                       or (self.data and self.data.get("active") and not active))
            if refresh:
                self._history = await self.client.charging_history(*month)
                self._history_month, self._history_fetched = month, now
            history = sorted(self._history, key=lambda x: str(x.get("startTime") or ""), reverse=True)
            return {"active": active, "history": history, "latest": history[0] if history else None}
        except EweGoAuthenticationError as exc:
            _LOGGER.warning("EWE Go authentication stage failed: %s", str(exc))
            raise ConfigEntryAuthFailed(str(exc)) from exc
        except EweGoApiError as exc:
            raise UpdateFailed(str(exc)) from exc
