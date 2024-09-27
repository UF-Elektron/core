from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant  # , callback?
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.components.valve import (
    ValveDeviceClass,
    ValveEntity,
    # ValveEntityDescription,
    ValveEntityFeature,
)

from .pypi.valves import Valve
from .pypi.ugw import ApiWithIni
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up valve for device."""

    bridge = hass.data[DOMAIN][entry.entry_id]
    # TODO: not every load entry in .devices is a motor but for now I don't care
    devices = bridge.api.devices

    """fixed ugw bastel"""
    api_object = ApiWithIni()

    # """Set up Example sensor based on a config entry."""
    # from https://developers.home-assistant.io/docs/core/entity
    # device: ExampleDevice = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        LisaValve(
            Valve(
                lisa_valve.get("id"),
                {
                    "name": lisa_valve.get("name", "missing name"),
                    "device": lisa_valve.get("device", "missing device address"),
                    "channel": lisa_valve.get("channel", "missing load channel"),
                    "type": lisa_valve.get("type", "missing load type"),
                    "sub_type": lisa_valve.get("sub_type", "missing sub type"),
                },
                api_object.req_data,
            )
        )
        for lisa_valve in devices
        if lisa_valve.get("type") in ["hvac"]
    )


class BaseEntity(Entity):
    def __init__(self, id, unique_name):
        # Entity class attributes
        # _attr_unique_id and / or _attr_device_info is needed so that the entity is connected with the device
        self._attr_unique_id = unique_name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, id)},
        )


class LisaValve(BaseEntity, ValveEntity):
    """Entity that controls a valve on block based Shelly devices."""

    _attr_device_class = ValveDeviceClass.WATER
    _attr_supported_features = ValveEntityFeature.OPEN | ValveEntityFeature.CLOSE

    def __init__(self, valve) -> None:
        """Initialize block valve."""
        self.valve = valve
        super().__init__(self.valve.id, self.valve.unique_name)
        self._attr_is_closed = True

    @property
    def is_closing(self) -> bool:
        """Return if the valve is closing."""
        return False

    @property
    def is_opening(self) -> bool:
        """Return if the valve is opening."""
        return False

    @property
    def reports_position(self) -> bool:
        return False

    async def async_open_valve(self, **kwargs) -> None:
        """Open valve."""
        print("TODO: implement open valve")

    async def async_close_valve(self, **kwargs) -> None:
        """Close valve."""
        print("TODO: implement close valve")

    # @callback
    # def _update_callback(self) -> None:
    #     """When device updates, clear control result that overrides state."""
    #     self.control_result = None
    #     self._attr_is_closed = bool(self.attribute_value == "closed")
    #     super()._update_callback()
