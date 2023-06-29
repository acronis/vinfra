import ipaddress
import json
import sys


# pylint: disable=no-name-in-module,import-error,unused-import,redefined-builtin,invalid-name

get_ipaddress_version = \
    lambda ipstr: ipaddress.ip_address(ipstr).version

if sys.version_info[0] == 2:
    from urlparse import parse_qs, urlparse
    from urllib2 import urlopen
    import cookielib

    get_ipaddress_version = \
        lambda ipstr: ipaddress.ip_address(unicode(ipstr)).version

    basestring = basestring

elif sys.version_info[0] == 3:
    from urllib.parse import parse_qs, urlparse
    from urllib.request import urlopen
    from http import cookiejar as cookielib

    basestring = str

JSONDecodeError = ValueError
try:
    # python3
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    pass
