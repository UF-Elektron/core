#! /usr/bin/env python3
# -----------------------------------------------------------------------------
#  @file  ./tests/api/utils.py
#
#  @brief  Helper functions for unit tests
#
#  @author  PES  antonio.pedrosa@anyweb.ch
#
#  @copyright  Copyright (C) 2019, Feller AG
# ------------------------------------------------------------------------------
#

"""Various utility functions."""

# Python module imports
import ssl
from configparser import ConfigParser

# Special requests module for HTTPS-Adapter
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager


class TLSv1Adapter(HTTPAdapter):
    """TLS V 1.0 Adapter

    GainSpan only works with TLS V1.0! Force to use TLS V1.0.
    """

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLSv1,
        )


def get_https_adapters():
    # Default: ssl.PROTOCOL_TLS_CLIENT (see: https://docs.python.org/3/library/ssl.html#ssl.PROTOCOL_TLS_CLIENT)
    # >>> from urllib3.util import ssl_
    # >>> sslctx = ssl_.create_urllib3_context(ssl_version=ssl_.resolve_ssl_version(None))
    # >>> sslctx.protocol
    # <_SSLMethod.PROTOCOL_TLS_CLIENT: 16>
    # >>> sslctx.options
    # <Options.OP_ALL|OP_NO_SSLv3|OP_CIPHER_SERVER_PREFERENCE|OP_ENABLE_MIDDLEBOX_COMPAT|OP_NO_COMPRESSION|OP_NO_TICKET: 2186428500>
    return {"tls_v1": TLSv1Adapter, "default": HTTPAdapter}


def plural(items, name):
    """Return correct plural of zero or more named items.

    :param items:  sequence of items or number of items
    :param name:  name of one single item
    :returns:  string with number and name, separated by one space
    """
    if not isinstance(items, int):
        items = len(items)
    return "%d %s%s" % (items, name, ("s", "")[items == 1])


def str2bool(bool_str):
    return str(bool_str).strip().lower() in ("true", "t", "yes", "y", "1")


def get_argv_from_config_file(inipath="./lgtests.ini"):
    # Set defaults
    argv = {
        "quiet": 0,
        "version": False,
        "help": False,
        "host": "192.168.0.1",
        "usessl": False,
        "verifysslcert": False,
        "ssladapter": "default",
        "fhxupgrade": False,
        "iothub_upgrade": False,
        "csaupgrade": False,
        "disabled_unittests": "",
        "botname": "",
        "logconf": None,
    }

    # Parse values from "lgtests.ini"
    config = ConfigParser()
    if not config.read(inipath):
        raise Exception('Can not read config-ini-file: "%s"' % inipath)
    else:
        for section in config.sections():
            argv.update(config.items(section))
        # Special handling of boolean values
        argv["usessl"] = str2bool(argv["usessl"])
        argv["verifysslcert"] = str2bool(argv["verifysslcert"])
        argv["fhxupgrade"] = str2bool(argv["fhxupgrade"])
        argv["iothub_upgrade"] = str2bool(argv["iothub_upgrade"])
        argv["csaupgrade"] = str2bool(argv["csaupgrade"])
        # Special handling of list values
        argv["disabled_unittests"] = argv["disabled_unittests"].split()
        # print('+inifile-argv = %s' % str(argv))

    return argv
