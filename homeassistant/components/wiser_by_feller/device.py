"""Handles lisa devices / loads and mapping to Home Assistant devices."""

from dataclasses import dataclass
from enum import Enum

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


class DeviceArchetypes(Enum):
    """Enum with all possible Device archetypes."""

    BRIDGE_V2 = "bridge_v2"
    UNKNOWN_ARCHETYPE = "unknown_archetype"


@dataclass
class DeviceProductData:
    """Represent a DeviceProductData object as used by the Hue api."""

    model_id: str
    software_version: str
    manufacturer_name: str
    product_name: str


@dataclass
class DeviceMetaData:
    """Represent MetaData for a device object as used by the Hue api."""

    # archetype: DeviceArchetypes
    name: str


@dataclass
class Device:
    """Blaaaablabla."""

    id: str
    product_data: DeviceProductData
    metadata: DeviceMetaData


# TODO: wie mappen wir am besten die source addresse, den load channel mit der load-id?
async def async_setup_devices(bridge):
    """Manage setup of devices from Hue devices."""
    entry = bridge.config_entry
    hass = bridge.hass
    api: ApiWithIni = bridge.api  # to satisfy typing
    dev_reg = dr.async_get(hass)
    # use test value
    # dev_controller = api.devices
    tmp_prod_data_1 = DeviceProductData("1", "2", "3", "4")
    tmp_meta_ugw = DeviceMetaData("ugw")
    a_ugw = Device("42", tmp_prod_data_1, tmp_meta_ugw)
    a_ugw.product_data.product_name = "test_name"
    a_ugw.product_data.model_id = "69"
    a_ugw.product_data.software_version = "1234"
    a_ugw.product_data.manufacturer_name = "chinesli"
    # a_ugw.metadata.name = "noname"

    tmp_prod_data_2 = DeviceProductData("9", "9", "9", "9")
    tmp_meta_device = DeviceMetaData("device")
    a_device = Device("5555", tmp_prod_data_2, tmp_meta_device)
    a_device.product_data.product_name = "device_blabla"
    a_device.product_data.model_id = "694288"
    a_device.product_data.software_version = "1234.5678"
    a_device.product_data.manufacturer_name = "-"
    # a_device.metadata.name = "noname"

    dev_controller = [a_ugw, a_device]
    # dev_controller = [
    #     {
    #         "product_data": {
    #             "product_name": "test_name",
    #             "model_id": "69",
    #             "software_version": "1234",
    #             "manufacturer_name": "chinesli",
    #         },
    #         "metadata": {"name": "noname"},
    #     }
    # ]

    # TODO: add type for "hue_resource", it used to be Device | Room | Zone
    @callback
    def add_device(hue_resource: Device) -> dr.DeviceEntry:
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
        # if hue_resource.metadata.archetype == DeviceArchetypes.BRIDGE_V2:
        if hue_resource.metadata.name == "ugw":
            print("attribute identified as ugw")
            params[ATTR_IDENTIFIERS].add((DOMAIN, api.bridge_id))
        else:
            print("attribute identified as device")
            # params[ATTR_VIA_DEVICE] = (DOMAIN, api.config.bridge_device.id)
            params[ATTR_VIA_DEVICE] = (DOMAIN, "3434343434343")  # id of uGW
        return dev_reg.async_get_or_create(config_entry_id=entry.entry_id, **params)

    known_devices = [add_device(hue_device) for hue_device in dev_controller]
