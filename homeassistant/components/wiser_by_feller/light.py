# PyPI imports

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityFeature,
    filter_supported_color_modes,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import Entity
from homeassistant.util.color import brightness_to_value

# testing: to create LisaLight in async_add_entities (TODO: remove)
from .pypi.lights import Light
from .pypi.ugw import ApiWithIni
from .const import DOMAIN

BRIGHTNESS_SCALE = (1, 10000)
MYLIGHT = None


@callback
def async_update_items(
    bridge, api, current, async_add_entities, create_item, new_items_callback
):
    """Update items."""
    new_items = []

    for item_id in api:
        if item_id in current:
            continue

        current[item_id] = create_item(api, item_id)
        new_items.append(current[item_id])

    if new_items:
        # This is currently used to setup the listener to update rooms
        if new_items_callback:
            new_items_callback()
        async_add_entities(new_items)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up light entities."""

    bridge = hass.data[DOMAIN][entry.entry_id]
    # TODO: not every load entry in .devices is a light but for now I don't care
    devices = bridge.api.devices

    """fixed ugw bastel"""
    api_object = ApiWithIni()

    # """Set up Example sensor based on a config entry."""
    # from https://developers.home-assistant.io/docs/core/entity
    # device: ExampleDevice = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        LisaLight(
            Light(
                lisa_light.get("id"),
                {
                    "name": lisa_light.get("name", "missing name"),
                    "device": lisa_light.get("device", "missing device address"),
                    "channel": lisa_light.get("channel", "missing load channel"),
                    "type": lisa_light.get("type", "missing load type"),
                    "sub_type": lisa_light.get("sub_type", "missing sub type"),
                },
                api_object.req_data,
            )
        )
        for lisa_light in devices
        if lisa_light.get("type") in ["onoff", "dim", "dali"]
    )
    # async_add_entities(make_light_entity(light) for light in controller)


class BaseEntity(Entity):
    def __init__(self, id, unique_name):
        # Entity class attributes
        # _attr_unique_id and / or _attr_device_info is needed so that the entity is connected with the device
        self._attr_unique_id = unique_name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, id)},
        )


class LisaLight(BaseEntity, LightEntity):
    """Representation of Lisa light."""

    # without coordinator for now
    # __init__(self, coordinator, light):
    def __init__(self, light):
        """Initialize the light."""
        self.light = light
        super().__init__(self.light.id, self.light.unique_name)

        # LightEntity class attributes

        set_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF
        if self.light.type in ["dim", "dali"]:
            set_supported_color_modes.add(ColorMode.BRIGHTNESS)
            self._attr_supported_features |= LightEntityFeature.TRANSITION
            self._attr_color_mode = ColorMode.BRIGHTNESS

        if self.light.sub_type in ["rgb"]:
            set_supported_color_modes.add(ColorMode.RGBW)
            self._attr_color_mode = ColorMode.RGBW
        elif self.light.sub_type in ["tw"]:
            set_supported_color_modes.add(ColorMode.WHITE)
            self._attr_color_mode = ColorMode.WHITE

        self._attr_supported_color_modes = filter_supported_color_modes(
            set_supported_color_modes
        )

    @property
    def available(self):
        """Return if light is available."""
        # TODO: implement available
        return True

    # Properties should always only return information from memory and not do I/O (like network requests).
    # Implement update() or async_update() to fetch data.

    @property
    def name(self):
        """Return the name of the Hue light."""
        return self.light.name

    @property
    def hs_color(self):
        """Return the hs color value."""
        return None

    @property
    def color_temp(self):
        return None

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        # TODO: implement is_on
        # TODO: add when scenes / groups are implemented
        # if self.is_group:
        #     return self.light.state["any_on"]
        return self.light.state

    def turn_on(self, **kwargs):
        """Turn device on."""
        ha_bri = kwargs.get(ATTR_BRIGHTNESS, 255)
        lisa_bri = int(brightness_to_value(BRIGHTNESS_SCALE, ha_bri))
        self.light.set_state({"bri": lisa_bri})

    def turn_off(self, **kwargs):
        """Turn device off."""
        data = {"bri": 0}
        self.light.set_state(data)

    # async def async_turn_on(self, **kwargs):
    #     """Turn device on."""
    #     # value_in_range = math.ceil(
    #     #     percentage_to_ranged_value(
    #     #         BRIGHTNESS_SCALE, kwargs.get(ATTR_BRIGHTNESS, 10000)
    #     #     )
    #     # )
    #     value_in_range = kwargs.get(ATTR_BRIGHTNESS, 10000)
    #     data = {"bri": value_in_range}
    #     self.light.async_set_state(data)

    # async def async_turn_off(self, **kwargs):
    #     """Turn device off."""
    #     data = {"bri": 0}
    #     self.light.async_set_state(data)
