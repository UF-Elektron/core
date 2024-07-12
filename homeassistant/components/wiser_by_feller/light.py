import math

# PyPI imports
from .pypi.lights import Light

from homeassistant.components.light import ATTR_BRIGHTNESS, LightEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.color import value_to_brightness
from homeassistant.util.percentage import percentage_to_ranged_value

from .pypi.ugw import ApiWithIni

BRIGHTNESS_SCALE = (1, 10000)
MYLIGHT = None

# cmd line testing
###################
# import asyncio
# import homeassistant.components.wiser_by_feller.light as light
# a_light = light.LisaLight(None)
# a_light.async_turn_on()


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Hue lights from a config entry."""
    # light1234 = LisaLight


def setup_entry():
    MYLIGHT = Light(10, {"name": "light 1"}, None)


class LisaLight(CoordinatorEntity, LightEntity):
    """Representation of Lisa light."""

    # without coordinator for now
    # __init__(self, coordinator, light):
    def __init__(self, light):
        """Initialize the light."""
        # super().__init__(coordinator)
        # self.light = light
        self.api_object = ApiWithIni()
        self.light = Light(10, {"name": "light 1"}, self.api_object.req_data)

    @property
    def name(self):
        """Return the name of the Hue light."""
        return self.light.name

    @property
    def brightness(self):
        """Return the current brightness."""
        return value_to_brightness(BRIGHTNESS_SCALE, self._device.brightness)

    @property
    def is_on(self):
        """Return true if device is on."""
        # TODO: add when scenes / groups are implemented
        # if self.is_group:
        #     return self.light.state["any_on"]
        print(f"is_on: {self.light.state}")
        return False

    def turn_on(self, **kwargs):
        """Turn device on."""
        value_in_range = kwargs.get(ATTR_BRIGHTNESS, 10000)
        data = {"bri": value_in_range}
        self.light.set_state(data)

    def turn_off(self, **kwargs):
        """Turn device off."""
        data = {"bri": 0}
        self.light.set_state(data)

    async def async_turn_on(self, **kwargs):
        """Turn device on."""
        # value_in_range = math.ceil(
        #     percentage_to_ranged_value(
        #         BRIGHTNESS_SCALE, kwargs.get(ATTR_BRIGHTNESS, 10000)
        #     )
        # )
        value_in_range = kwargs.get(ATTR_BRIGHTNESS, 10000)
        data = {"bri": value_in_range}
        self.light.async_set_state(data)

    async def async_turn_off(self, **kwargs):
        """Turn device off."""
        data = {"bri": 0}
        self.light.async_set_state(data)
