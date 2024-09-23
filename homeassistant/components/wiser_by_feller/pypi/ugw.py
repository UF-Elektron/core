"""Base class for REST-API UnitTests."""
# TODO: move this to __init__.py for PyPI

# Python module imports
import os
import time

import requests

# Import local modules
from . import utils

# Version of this tool, printed with option "--version"
__version__ = "20240418.0"


# uGW FWIDs stuff
UGW_FWID_V1 = 0x8692
UGW_FWID_V2 = 0x8694

# Get HTTPS-Adapters
HTTPS_ADAPTERS = utils.get_https_adapters()


# from TestCaseRestApiWithIni
class ApiWithIni:
    """Default TestCase for API-UnitTests using module 'requests' (see 'http://2.python-requests.org/en/latest').

    Small configuration possible in file 'lgtests.ini'.

    Per default we call one HTTP(S)-request (requests.Request) per API-Call.

    So if you're making several requests to the same host,
    its possible to use the 'requests.Session' object.
    The underlying TCP connection will be reused,
    which can result in a significant performance increase
    (see HTTP persistent connection 'https://en.wikipedia.org/wiki/HTTP_persistent_connection').
    """

    request_session = None
    request_retries = 3
    use_request_session = True
    api_entry_point_folder = "api"

    # Add here expected data key-attributes and (python-data)-types e.g. {'id': str}
    required_attr_types = None

    def __init__(self):
        print("setup class")

        # Read about 'request-session'
        # http://2.python-requests.org/en/latest/user/advanced/#session-objects
        if not self.request_session and self.use_request_session:
            self.request_session = requests.Session()

        # **start** copy of hue PyPI stuff
        # ------------------------------------------------------------
        self._devices = None
        # TODO: implement DevicesController:
        # self._devices = DevicesController(self)

    # ...copy of hue PyPI stuff
    # ------------------------------------------------------------

    # TODO: add return type  -> DevicesController:
    @property
    def devices(self):
        """Get the Devices Controller for managing all device resources."""
        # return self._devices
        place_holder_loads = [
            {
                "id": 10,
                "unused": False,
                "name": "B%C3%BCro%20(Steckdose)",
                "room": "Home",  # room is actualy an ID and name needs to retrieved from rooms object
                "type": "onoff",
                "device": "00019eb8",
                "channel": 0,
                "sub_type": "",
                # load enrichement
                "manufacterer": "Feller AG",
                "sw_ver": "A: 2.0.6-0, C: 1.8.3-0",
                "hw_id": "0x1113",
                "is_ugw": False,
            },
            {
                "id": 8,
                "unused": False,
                "name": "Esstisch",
                "room": "Home",
                "type": "onoff",
                "device": "00019ea5",
                "channel": 0,
                "sub_type": "",
                # load enrichement
                "manufacterer": "Feller AG",
                "sw_ver": "A: 2.0.6-0, C: 1.8.3-0",
                "hw_id": "0x1113",
                "is_ugw": True,  # TODO: currently this does not work and joins all is_ugw True entities together and not to uGW device
            },
            {
                "id": 12,
                "unused": False,
                "name": "Fake Dimmer",
                "room": "Home",
                "type": "dim",
                "device": "00012345",
                "channel": 0,
                "sub_type": "",
                # load enrichement
                "manufacterer": "Feller AG",
                "sw_ver": "A: 2.0.6-0, C: 1.8.3-0",
                "hw_id": "0x1213",
                "is_ugw": False,
            },
        ]
        return place_holder_loads

    @property
    def bridge_id(self) -> str | None:
        """Return the ID of the bridge we're currently connected to."""
        # TODO: get real ID from uGW
        return "made_up_ID_for_ugw"

    @property
    def config(self):  # -> ConfigController:
        """Get the Config Controller with config-like resources."""
        return self._config

    # **end** copy of hue PyPI stuff
    # ------------------------------------------------------------

    def req(self, method, subpath, **kwargs):
        # Read options
        lisagateway_host = self.argv.get("host", "127.0.0.1")
        lisagateway_usessl = bool(self.argv.get("usessl", False))
        lisagateway_verifysslcert = bool(self.argv.get("verifysslcert", False))

        lisagateway_api_url = "http{}://{}/{}".format(
            ["", "s"][lisagateway_usessl], lisagateway_host, self.api_entry_point_folder
        )

        # Set a default-timeout
        kwargs["timeout"] = kwtimeout = kwargs.get("timeout", 15)

        # Get hooks for pretty logging
        # request_logging_hook = get_request_logging_hook()
        # if request_logging_hook:
        #     # Append logger-magic to requests-hooks
        #     kwargs["hooks"] = kwargs.get("hooks", {})
        #     hooks_response = kwargs["hooks"].get("response", [])
        #     if not isinstance(hooks_response, list):
        #         hooks_response = [hooks_response]
        #     hooks_response.append(request_logging_hook)
        #     kwargs["hooks"]["response"] = hooks_response

        # Set option for literal URL
        literal_url = kwargs.pop("literal_url", False)

        if lisagateway_usessl or literal_url:
            if not self.request_session:
                self.request_session = requests.Session()
            https_adapter = HTTPS_ADAPTERS[self.argv.get("ssladapter", "default")]
            self.request_session.mount("https://", https_adapter())

        retry = max(self.request_retries, 1)
        while True:
            try:
                lisagateway_api_url_full = "%s%s" % (lisagateway_api_url, subpath)

                # Using 'request.session'
                # The Session object allows you to persist
                # certain parameters across requests.
                if self.request_session:
                    # Remove attribute(s) for call 'requests.Request'
                    kwargs.pop("timeout", None)

                    # Request with session object
                    req = requests.Request(method, lisagateway_api_url_full, **kwargs)

                    prepped_req = req.prepare()
                    if literal_url:
                        # Overwrite prepared URL with original (to keep dots etc.)
                        prepped_req.url = lisagateway_api_url_full

                    resp = self.request_session.send(
                        prepped_req, timeout=kwtimeout, verify=lisagateway_verifysslcert
                    )
                else:
                    # Default request
                    resp = requests.request(method, lisagateway_api_url_full, **kwargs)

                break
            except requests.RequestException:
                retry -= 1
                if not retry:
                    raise
        return resp

    def req_jsend(self, method, subpath, **kwargs):
        resp = self.req(method, subpath, **kwargs)
        assert resp.status_code == 200, f"response status {resp.status_code}"
        return resp.json()

    def devices_manage_single_register(
        self,
        api_method="GET",
        rheaders=None,
        request_props=None,
        expect_data=None,
        device_id=None,
        device_block="a",
        device_reg_address=None,
    ):
        api_path = f"/devices/{device_id}/register/{device_block}/{device_reg_address}"
        data = self.req_data(
            "PUT",
            api_path,
            headers=rheaders,
            json=request_props,
        )
        return data

    def tmp_set_target_state(self, id, data=None):
        jsend_data = self.req_data("put", f"/loads/{id}/target_state", json=data)
        print(jsend_data)

    def req_data(self, method, subpath, **kwargs):
        jsend = self.req_jsend(method, subpath, **kwargs)

        assert "status" in jsend, f"{jsend}"
        assert "success" == jsend["status"], f"{jsend}"
        assert "data" in jsend, f"{jsend}"

        return jsend["data"]

    def get_ugw_fwid(self):
        return (
            UGW_FWID_V2
            if "H753" in self.req_data("GET", "/info/debug")["hw"]
            else UGW_FWID_V1
        )

    def is_ugw_hw_v1(self):
        return self.get_ugw_fwid() == UGW_FWID_V1

    def is_ugw_hw_v2(self):
        return self.get_ugw_fwid() == UGW_FWID_V2

    def wait_for_reboot(self, timeout=90):
        # Wait 10 sec and then poll GET /api/info
        resp = None
        end_time = time.time() + timeout
        time.sleep(10)
        while time.time() < end_time:
            try:
                # Poll every 3 sec
                resp = self.req_data("GET", "/info", timeout=3)
                if resp:
                    break
            except OSError:
                pass
        else:
            self.fail("Timeout after waiting for reboot")
        return resp

    def class_init():
        """Read testing parameters from ini-file and command line."""

        dirname = os.path.dirname(os.path.abspath(__file__))
        # Default of config-INI-file
        config_ini_default_path = os.path.join(dirname, "lgtests.ini")
        config_ini_argv = {}

        config_ini_argv = utils.get_argv_from_config_file(config_ini_default_path)

        # Configure loggers
        # logconf = config_ini_argv.get("logconf")
        # if logconf:
        #     with open(logconf) as logger_config_json:
        #         logging.config.dictConfig(json.load(logger_config_json))

        #     # Custom logging-magic
        #     import logging_helper

        #     logging_helper.init()

        return config_ini_argv, dirname

    argv, dirname = class_init()
