"""TODO: move to pyPI package."""

from collections.abc import Coroutine


# not used jet... in components/wiser_by_feller/light.py the LisaLight needs to be iterable...
class Lights:
    """Represents Lights"""

    def __init__(self, raw, request: Coroutine) -> None:
        """Initialize instance."""
        self._request = request
        self._item_cls = Light
        self._items = {}
        for id_1, raw_item in raw.items():
            obj = self._items.get(id_1)

            if obj is not None:
                obj.raw = raw_item
            else:
                self._items[id_1] = self._item_cls(
                    id_1,
                    raw_item,
                    self._request,
                )

    @property
    def items(self):
        return self.values()

    def values(self):
        return list(self._items.values())

    def __getitem__(self, obj_id):
        return self._items[obj_id]

    def __iter__(self):
        return iter(self._items)


class Light:
    """Represents a WbF light."""

    def __init__(self, id: str, raw, request: Coroutine) -> None:
        """Initialize instance."""
        print(f"init 'Light' with '{id=}', '{raw=}'")
        self._id = id
        self.raw = raw
        self._request = request
        # self._request = self.api_object.tmp_set_target_state
        # TODO: remove testing variable, also remove from properties
        self._tmp_state_testing = False

    @property
    def name(self):
        return self.raw["name"]

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
