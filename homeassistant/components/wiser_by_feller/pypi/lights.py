"""TODO: move to pyPI package."""

from collections.abc import Coroutine


class Light:
    """Represents a WbF light."""

    ITEM_TYPE = "lights"

    def __init__(self, id: str, raw, request: Coroutine) -> None:
        """Initialize instance."""
        self.id = id
        self.raw = raw
        self._request = request
        # self._request = self.api_object.tmp_set_target_state

    @property
    def name(self):
        return self.raw["name"]

    @property
    def state(self):
        return "state not implemented"

    def set_state(self, data):
        """Change state of a light."""
        # jsend_data = self.api_object.req_data("put", f"/loads/{self.id}/target_state", json=data)
        jsend_data = self._request("put", f"/loads/{self.id}/target_state", json=data)

    async def async_set_state(self, data):
        """Change state of a light."""
        # jsend_data = self.api_object.req_data("put", f"/loads/{self.id}/target_state", json=data)
        jsend_data = self._request("put", f"/loads/{self.id}/target_state", json=data)
