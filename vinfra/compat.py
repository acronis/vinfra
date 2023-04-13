import sys

# pylint: disable=no-name-in-module,import-error,unused-import

if sys.version_info[0] == 2:
    from urlparse import urlparse
    from urllib2 import urlopen, addinfourl
    from md5 import md5
    from httplib import HTTPResponse
    from urllib import urlencode

elif sys.version_info[0] == 3:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, addinfourl
    from hashlib import md5
    from http.client import HTTPResponse
