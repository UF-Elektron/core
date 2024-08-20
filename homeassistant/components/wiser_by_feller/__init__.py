"""The Wiser by Feller integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .ugw import LisaGateway

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.LIGHT]

# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations
# type New_NameConfigEntry = ConfigEntry[MyApi]  # noqa: F821


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wiser by Feller from a config entry."""

    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # entry.runtime_data = MyAPI(...)

    # DME: will be done in ugw.py: async_initialize_bridge
    # await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # TODO: rename
    bridge = LisaGateway(hass, entry)
    if not await bridge.async_initialize_bridge():
        return False

    # hass.states.async_set("wiser_by_feller.Hello_World", "Works :-) !")

    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
