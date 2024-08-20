from homeassistant import core
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_API_VERSION, CONF_HOST, Platform

from .const import DOMAIN
from .pypi.ugw import ApiWithIni

# TODO: soll ich PLATFORMS hier wie bei hue machen, oder wie von HA vorgeschlagen in __init__.py?
# jetzt 2 mal...
PLATFORMS: list[Platform] = [Platform.LIGHT]


# DME: stolen from hue/bridge.py
class LisaGateway:
    """Manages a single Lisa Gateway."""

    def __init__(self, hass: core.HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the system."""
        self.config_entry = config_entry
        self.hass = hass
        # TODO: __init__.py of PyPI project where HueBridgeV2 is object to control uGW
        # self.api = HueBridgeV2(self.host, app_key)
        # something like this...
        api_object = ApiWithIni()
        hass.data.setdefault(DOMAIN, {})[self.config_entry.entry_id] = self

    @property
    def host(self) -> str:
        """Return the host of this bridge."""
        return self.config_entry.data[CONF_HOST]

    @property
    def api_version(self) -> int:
        """Return api version we're set-up for."""
        return self.config_entry.data[CONF_API_VERSION]

    # TODO: rename function
    async def async_initialize_bridge(self) -> bool:
        """Initialize Connection with the Hue API."""
        # TODO: initialisierungs code
        # ... api.init()
        # return False if uGW initialization failed
        # before return False throw an exception like this: self.logger.exception("Unknown error connecting to Hue bridge")
        # TODO: setup devices
        # await async_setup_devices(self)

        # forward my config entry to home assistant
        await self.hass.config_entries.async_forward_entry_setups(
            self.config_entry, PLATFORMS
        )
        return True


# TODO: es gibt in bridge.py noch mehr funktionen, die sollten aber für den Anfang noc nicht nötig sein
# wobei "async_request_call" könnte noch wichtig sein...
# async def async_request_call(self, task: Callable, *args, **kwargs) -> Any:
#     """Send request to the Hue bridge."""
