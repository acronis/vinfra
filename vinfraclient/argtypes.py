import argparse
from argparse import ArgumentTypeError


def parse_dict_options(value, optional_keys=None):
    optional_keys = set(optional_keys or [])
    res = {}
    for arg in value.split(','):
        msg = "{!r} is not a 'key=value' pair".format(arg)
        try:
            key, val = arg.split('=', 1)
            if not val or key == '':
                raise argparse.ArgumentTypeError(msg)
        except ValueError:
            raise argparse.ArgumentTypeError(msg)
        res[key] = val

    if optional_keys:
        invalid_keys = [k for k in res if k not in optional_keys]
        if invalid_keys:
            raise argparse.ArgumentTypeError(
                "Invalid keys {invalid_keys} specified.\n"
                "Valid keys are: {valid_keys}".format(
                    invalid_keys=', '.join(invalid_keys),
                    valid_keys=', '.join(optional_keys)))
    return res


def parse_pair_options(value):
    res = []
    for arg in value.split(','):
        msg = "{!r} is not a 'key=value' pair".format(arg)
        try:
            key, val = arg.split('=', 1)
            if not val:
                raise argparse.ArgumentTypeError(msg)
        except ValueError:
            raise argparse.ArgumentTypeError(msg)
        res.append((key, val))
    return res


def parse_list_options(value):
    res = []
    for arg in value.split(','):
        if not arg:
            continue
        res.append(arg)
    return res


class ValueType(object):
    def __call__(self, value):
        raise NotImplementedError('.__call__() not defined')


class BoolType(ValueType):
    def __call__(self, value):
        v = value.lower()
        if v in ['true', 'on', 'yes', '1']:
            return True
        if v in ['false', 'off', 'no', '0']:
            return False

        raise ArgumentTypeError("invalid format: {} (choose from true,false,"
                                "on,off,yes,no,1,0)".format(value))


class ChoicesType(ValueType):
    def __init__(self, choices):
        self._choices = choices

    def __call__(self, value):
        if value not in self._choices:
            raise ArgumentTypeError(
                "invalid choice {!r} (choose from {})".format(
                    value, ', '.join(self._choices))
            )
        return value


class MultiChoicesType(ValueType):
    def __init__(self, choices):
        self._choices = choices

    def __call__(self, value):
        array = parse_list_options(value)
        result = []
        for item in array:
            if item not in self._choices:
                raise ArgumentTypeError(
                    "invalid choice {!r} (choose from {})".format(
                        item, ', '.join(self._choices))
                )
            result.append(item)
        return result


class StructType(ValueType):
    def __init__(self, **kwargs):
        self._kwtypes = kwargs
        self.skip_types_check = False

    def __call__(self, value):
        res = {}
        for kv_str in value.split(","):
            if '=' not in kv_str:
                raise ArgumentTypeError(
                    "{!r} value format error. (format "
                    "key1=value1[,key2=value2...])".format(kv_str)
                )
            key, val = kv_str.split('=', 1)
            if self.skip_types_check:
                res[key] = val
                continue
            if key not in self._kwtypes:
                raise ArgumentTypeError(
                    "unrecognized argument: {}".format(key))

            type_func = self._kwtypes[key]
            if not hasattr(type_func, '__call__'):
                raise ArgumentTypeError(
                    "{!r} is not callable".format(type_func)
                )
            try:
                res[key] = type_func(val)
            except ValueError:
                raise ArgumentTypeError("invalid format: {!r}".format(kv_str))

        return res


class StructTypeSkipCheck(StructType):
    def __init__(self, **kwargs):
        StructType.__init__(self, **kwargs)
        self.skip_types_check = True


boolean = BoolType()


def choice(choices):
    return ChoicesType(choices)


def multi_choice(choices):
    return MultiChoicesType(choices)


def struct(**kwargs):
    return StructType(**kwargs)


def non_empty_string(value):
    if not value:
        raise ArgumentTypeError("must not be empty string")
    return value


def size_limited_string(value, chars_limit):
    if len(value) > chars_limit:
        raise ArgumentTypeError("max string length is %i" % chars_limit)
    return value
