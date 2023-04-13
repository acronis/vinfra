import collections
import functools
import re

from vinfra import exceptions


_METHODS = collections.defaultdict(list)
Method = collections.namedtuple('Method', ['name', 'func', 'start_version',
                                           'end_version'])


class APIVersion(object):
    def __init__(self, version):
        self.version = version
        match = re.match(r"^(\d+|latest)\.(\d+|latest)\.(\d+|latest)$", version)
        if not match:
            raise exceptions.VinfraError(
                "Invalid format of version {}".format(version))

        def ver_to_int(ver):
            if ver == 'latest':
                return float("inf")
            return int(ver)

        self.ver_major = ver_to_int(match.group(1))
        self.ver_middle = ver_to_int(match.group(2))
        self.ver_minor = ver_to_int(match.group(3))

    @classmethod
    def from_string(cls, version, extend_by=None):
        ver_points = version.count('.')
        if ver_points < 2:
            if not extend_by:
                raise exceptions.VinfraError(
                    "Invalid format of version {}".format(version))
            version = "{}.{}".format(version, extend_by)
            return cls.from_string(version, extend_by=extend_by)

        return cls(version)

    def __lt__(self, other):
        if isinstance(other, (str, basestring)):
            other = APIVersion(other)

        assert isinstance(other, APIVersion)
        return ((self.ver_major, self.ver_middle, self.ver_minor) <
                (other.ver_major, other.ver_middle, other.ver_minor))

    def __eq__(self, other):
        if isinstance(other, (str, basestring)):
            other = APIVersion(other)

        assert isinstance(other, APIVersion)
        return ((self.ver_major, self.ver_middle, self.ver_minor) ==
                (other.ver_major, other.ver_middle, other.ver_minor))

    def __gt__(self, other):
        if isinstance(other, (str, basestring)):
            other = APIVersion(other)

        assert isinstance(other, APIVersion)
        return ((self.ver_major, self.ver_middle, self.ver_minor) >
                (other.ver_major, other.ver_middle, other.ver_minor))

    def __le__(self, other):
        return self < other or self == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __ge__(self, other):
        return self > other or self == other


def _get_methods(func_name, api_version):

    def match_version(method):
        return method.start_version <= api_version <= method.end_version

    methods = _METHODS.get(func_name, [])
    methods = list(filter(match_version, methods))
    return methods


def version_wrap(start_version, end_version="latest"):
    start_version = APIVersion.from_string(start_version, extend_by='0')
    end_version = APIVersion.from_string(end_version, extend_by='latest')

    def wrapper(func):
        func_name = "%s.%s" % (func.__module__, func.__name__)

        method = Method(func_name, func, start_version, end_version)
        _METHODS[func_name].append(method)

        @functools.wraps(func)
        def inner(obj, *args, **kwargs):
            methods = _get_methods(func_name, obj.api.api_version)
            if not methods:
                raise exceptions.VinfraError(
                    "Function {!r} not found for version {}"
                    .format(func_name, obj.api.api_version))

            return methods[-1].func(obj, *args, **kwargs)

        return inner

    return wrapper


# NB: APIVersion should be a backend API version
HCI_VER_30 = APIVersion('2.3.0')
HCI_VER_35 = APIVersion('3.0.0')
HCI_VER_40 = APIVersion('4.0.0')
HCI_VER_45 = APIVersion('4.5.0')
HCI_VER_46 = APIVersion('4.6.0')
HCI_VER_47 = APIVersion('4.7.0')
HCI_VER_50 = APIVersion('5.0.0')
HCI_VER_51 = APIVersion('5.1.0')
HCI_VER_52 = APIVersion('5.2.0')
