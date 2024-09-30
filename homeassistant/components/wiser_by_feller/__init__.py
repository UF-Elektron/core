"""The Wiser by Feller integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .ugw import LisaGateway

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.COVER, Platform.VALVE]

# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations
# type New_NameConfigEntry = ConfigEntry[MyApi]  # noqa: F821
from .pypi.ugw import ApiWithIni


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
    # TODO: replace place holder
    # api = bridge.api
    api: ApiWithIni = bridge.api
    ugw_controller = api.ugw
    if not await bridge.async_initialize_bridge():
        return False

    # add bridge device to device registry
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        connections={
            (
                dr.CONNECTION_NETWORK_MAC,
                ugw_controller.get("mac_address", "missing MAC!!!"),
            )
        },
        identifiers={(DOMAIN, ugw_controller.get("ugw_id", "missing ugw_id"))},
        manufacturer=ugw_controller.get("manufacturer", "missing manufucturer"),
        name=ugw_controller.get("name", "missing name"),
        model=ugw_controller.get("type", "missing type"),
        sw_version=ugw_controller.get("sw_ver", "missing sw_ver"),
    )
    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
