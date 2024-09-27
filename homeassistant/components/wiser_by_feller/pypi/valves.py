"""TODO: move to pyPI package."""

from collections.abc import Coroutine


class Valve:
    """Represents a WbF valve."""

    def __init__(self, id: str, raw, request: Coroutine) -> None:
        """Initialize instance."""
        print(f"init 'Valve' with '{id=}', '{raw=}'")
        self._id = id
        self.raw = raw
        self._unique_name = f"{raw['device']}_{raw['channel']}"
        self._request = request
        # self._request = self.api_object.tmp_set_target_state
        # TODO: remove testing variable, also remove from properties
        self._tmp_state_testing = False

    @property
    def unique_name(self):
        return self._unique_name

    @property
    def id(self):
        print(f"return id {self._id}")
        return self._id

    @property
    def name(self):
        return self.raw["name"]

    @property
    def type(self):
        return self.raw["type"]

    @property
    def sub_type(self):
        return self.raw["sub_type"]

    @property
    def state(self):
        print("call property state of Light")
        return self._tmp_state_testing

    def set_state(self, data):
        """Change state of a light."""
        self._tmp_state_testing = data.get("bri", 0) > 0
        jsend_data = self._request("put", f"/loads/{self._id}/target_state", json=data)

    async def async_set_state(self, data):
        """Change state of a light."""
        self._tmp_state_testing = data.get("bri", 0) > 0
        jsend_data = self._request("put", f"/loads/{self._id}/target_state", json=data)
