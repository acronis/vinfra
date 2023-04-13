from vinfra import exceptions


def flatten_args(**kwargs):
    """ Return kwargs where value is not None.
    """
    return dict((k, v) for (k, v) in kwargs.items() if v is not None)


def only_obj(lst, msg=""):
    if len(lst) != 1:
        raise Exception(
            "Unexpected elememts count={0}. ".format(len(lst)) + msg
        )

    return lst[0]


def first(iterable, default=None):
    rv = next(iter(iterable), default)
    return rv


def get_stream(stream):
    if not hasattr(stream, 'read'):
        try:
            stream = open(stream, 'rb')
        except Exception as err:
            raise exceptions.VinfraError(err)
    return stream
