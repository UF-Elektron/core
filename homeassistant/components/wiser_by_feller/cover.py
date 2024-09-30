from homeassistant.components.cover import (
    CoverEntity,
    CoverDeviceClass,
    CoverEntityFeature,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant  # + callback?
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import Entity


from .pypi.motors import Motor
from .pypi.ugw import ApiWithIni
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up cover entities."""

    bridge = hass.data[DOMAIN][entry.entry_id]
    # TODO: not every load entry in .devices is a motor but for now I don't care
    devices = bridge.api.devices

    """fixed ugw bastel"""
    api_object = ApiWithIni()

    # """Set up Example sensor based on a config entry."""
    # from https://developers.home-assistant.io/docs/core/entity
    # device: ExampleDevice = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        LisaCover(
            Motor(
                lisa_motor.get("id"),
                {
                    "name": lisa_motor.get("name", "missing name"),
                    "device": lisa_motor.get("device", "missing device address"),
                    "channel": lisa_motor.get("channel", "missing load channel"),
                    "type": lisa_motor.get("type", "missing load type"),
                    "sub_type": lisa_motor.get("sub_type", "missing sub type"),
                },
                api_object.req_data,
            )
        )
        for lisa_motor in devices
        if lisa_motor.get("type") in ["motor"]
    )


class BaseEntity(Entity):
    def __init__(self, id, unique_name):
        # Entity class attributes
        # _attr_unique_id and / or _attr_device_info is needed so that the entity is connected with the device
        self._attr_unique_id = unique_name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, id)},
        )


class LisaCover(BaseEntity, CoverEntity):
    """Representation of Lisa cover / motor entity."""

    _attr_supported_features: CoverEntityFeature = (
        CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
    )

    # without coordinator for now
    # __init__(self, coordinator, cover):
    def __init__(self, cover):
        """Initialize the cover."""
        self.cover = cover
        super().__init__(self.cover.id, self.cover.unique_name)

        # CoverEntity class attributes
        self._attr_device_class = CoverDeviceClass.BLIND  # vielleicht auch SHUTTER...
        # if no tilt go for CoverDeviceClass.AWNING
        # no clue what to do for relay mode, probably use CoverDeviceClass.AWNING

    @property
    def is_closed(self) -> bool:
        """If cover is closed."""
        return True

    @property
    def current_cover_position(self) -> int:
        """Position of the cover."""
        return 0

    @property
    def is_closing(self) -> bool:
        """Return if the cover is closing."""
        return False

    @property
    def is_opening(self) -> bool:
        """Return if the cover is opening."""
        return False

    # Properties should always only return information from memory and not do I/O (like network requests).
    # Implement update() or async_update() to fetch data.
