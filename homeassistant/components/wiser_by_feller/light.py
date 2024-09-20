# PyPI imports

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.color import value_to_brightness

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
    # # from https://developers.home-assistant.io/docs/core/entity
    # # device: ExampleDevice = hass.data[DOMAIN][entry.entry_id]
    # device: ExampleDevice = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        LisaLight(
            Light(
                lisa_light.get("id"),
                {"name": lisa_light.get("name")},
                api_object.req_data,
            )
        )
        for lisa_light in devices
    )
    # async_add_entities(make_light_entity(light) for light in controller)


# add coordinator later
# class LisaLight(CoordinatorEntity, LightEntity):
class LisaLight(LightEntity):
    """Representation of Lisa light."""

    # without coordinator for now
    # __init__(self, coordinator, light):
    def __init__(self, light):
        """Initialize the light."""
        print("create a LisaLight")
        # super().__init__(coordinator)
        self.light = light
        # self.api_object = ApiWithIni()
        # self.light = Light(10, {"name": "light 1"}, self.api_object.req_data)
        self._attr_supported_color_modes = {ColorMode.ONOFF}

    @property
    def available(self):
        """Return if light is available."""
        print("'available' not implemented")
        return True

    # Properties should always only return information from memory and not do I/O (like network requests).
    # Implement update() or async_update() to fetch data.

    @property
    def name(self):
        """Return the name of the Hue light."""
        return self.light.name

    @property
    def brightness(self):
        """Return the current brightness."""
        return value_to_brightness(BRIGHTNESS_SCALE, self._device.brightness)

    @property
    def color_mode(self) -> str:
        """Return the color mode of the light."""
        return ColorMode.ONOFF

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
        # TODO: add when scenes / groups are implemented
        # if self.is_group:
        #     return self.light.state["any_on"]
        print(f"is_on: {self.light.state}")
        return self.light.state

    def turn_on(self, **kwargs):
        """Turn device on."""
        value_in_range = kwargs.get(ATTR_BRIGHTNESS, 10000)
        data = {"bri": value_in_range}
        self.light.set_state(data)

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
