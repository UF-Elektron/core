"""Handles lisa devices / loads and mapping to Home Assistant devices."""

# code from hue/v2/device.py
# maybe better name load / loads? name device.py
from homeassistant.const import (
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_SW_VERSION,
    ATTR_VIA_DEVICE,
)
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .pypi.ugw import ApiWithIni
from .ugw import LisaGateway


async def async_setup_devices(bridge: LisaGateway):
    """Manage setup of devices from Hue devices."""
    entry = bridge.config_entry
    hass = bridge.hass
    api: ApiWithIni = bridge.api  # to satisfy typing
    dev_reg = dr.async_get(hass)
    dev_controller = api.devices

    # TODO: add type for "hue_resource", it used to be Device | Room | Zone
    @callback
    def add_device(hue_resource) -> dr.DeviceEntry:
        """Register a Hue device in device registry."""
        # Register a Hue device resource as device in HA device registry.
        model = f"{hue_resource.product_data.product_name} ({hue_resource.product_data.model_id})"
        params = {
            ATTR_IDENTIFIERS: {(DOMAIN, hue_resource.id)},
            ATTR_SW_VERSION: hue_resource.product_data.software_version,
            ATTR_NAME: hue_resource.metadata.name,
            ATTR_MODEL: model,
            ATTR_MANUFACTURER: hue_resource.product_data.manufacturer_name,
        }
        # DME: is it a normal device or the uGateway? copy from hue devices.py
        # for now handle it like it's always a bridge/uGW
        # if hue_resource.metadata.archetype == DeviceArchetypes.BRIDGE_V2:
        #     params[ATTR_IDENTIFIERS].add((DOMAIN, api.config.bridge_id))
        # else:
        #     params[ATTR_VIA_DEVICE] = (DOMAIN, api.config.bridge_device.id)
        params[ATTR_IDENTIFIERS].add((DOMAIN, api.config.bridge_id))
        return dev_reg.async_get_or_create(config_entry_id=entry.entry_id, **params)

    known_devices = [add_device(hue_device) for hue_device in dev_controller]
