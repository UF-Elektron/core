"""Config flow for Wiser by Feller integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components import zeroconf
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        print(f"try to authenticate with {username=} {password=} on {self.host=}")
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )

    hub = PlaceholderHub(data[CONF_HOST])

    if not await hub.authenticate(data[CONF_USERNAME], data[CONF_PASSWORD]):
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "μGW V2"}


class WbfConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wiser by Feller."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """Get the options flow for this handler."""

        return HueV2OptionsFlowHandler(config_entry)

    def __init__(self) -> None:
        """Initialize the Hue flow."""
        print("WbfConfigFlow __init__: nothing to do here")

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        print(f"async_step_user: {user_input=}")
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Empty: abort."""
        return self.async_abort(reason="cannot_connect")

    async def async_step_homekit(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Empty: abort."""
        return self.async_abort(reason="cannot_connect")

    async def async_step_import(self, import_info: dict[str, Any]) -> ConfigFlowResult:
        """Empty: abort."""
        return self.async_abort(reason="cannot_connect")


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class HueV2OptionsFlowHandler(OptionsFlow):
    """Handle Hue options for V2 implementation."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize Hue options flow."""
        print("HueV2OptionsFlowHandler...")
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage Hue options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        # TODO: other handling needed?
        return self.async_create_entry(title="", data=user_input)
