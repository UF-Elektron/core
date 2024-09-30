"""Handles lisa devices / loads and mapping to Home Assistant devices."""

# code from hue/v2/device.py
# maybe better name load / loads? name device.py
from homeassistant.const import (
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
    # use rooms id from load object for suggested area (room name is in rooms object)
    # ATTR_SUGGESTED_AREA,
    ATTR_SW_VERSION,
    ATTR_VIA_DEVICE,
)
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .pypi.ugw import ApiWithIni

# it's anyway only used "if TYPE_CHECKING" in hue project
# devices.py gets importet by ugw.py and ugw.py by __init__.py. Both ugw.py and devices.py import LisaGateway: circular import!
# from .ugw import LisaGateway
# does not work with this either
# from . import ugw


async def async_setup_devices(bridge):
    """Manage setup of devices from Hue devices."""
    entry = bridge.config_entry
    hass = bridge.hass
    api: ApiWithIni = bridge.api  # to satisfy typing
    dev_reg = dr.async_get(hass)
    dev_controller = api.devices
    ugw_controller = api.ugw  # used to add via_device ugw_id

    # TODO: add type for "hue_resource", it used to be Device | Room | Zone
    @callback
    def add_device(lisa_load) -> dr.DeviceEntry:
        """Register a Hue device in device registry."""
        model = f"{lisa_load.get("type")} ({lisa_load.get("hw_id")})"
        params = {
            ATTR_IDENTIFIERS: {(DOMAIN, lisa_load.get("id"))},
            ATTR_SW_VERSION: lisa_load.get("sw_ver"),
            ATTR_NAME: lisa_load.get("name"),
            ATTR_MODEL: model,
            ATTR_MANUFACTURER: lisa_load.get("manufacterer"),
        }

        params[ATTR_VIA_DEVICE] = (
            DOMAIN,
            ugw_controller.get("ugw_id", "missing ugw_id"),
        )
        return dev_reg.async_get_or_create(config_entry_id=entry.entry_id, **params)

    known_devices = [add_device(lisa_load) for lisa_load in dev_controller]
