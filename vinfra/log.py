import logging
import sys
import threading

root_logger = logging.getLogger()
_log_context = threading.local()


class Formatter(logging.Formatter):
    def format(self, record):
        record.request_id = get_request_id() or '-'
        self._fmt = ("%(asctime)s %(levelname)-8s %(name)s [%(request_id)s] "
                     "%(message)s")

        return super(Formatter, self).format(record)


def set_request_id(request_id):
    _log_context.request_id = request_id


def get_request_id():
    return getattr(_log_context, 'request_id', None)


def setup(filename=None, stream=None, log_level=logging.WARNING):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    if filename:
        file_handler = logging.FileHandler(filename=filename)
        # Always log with a debug level to the file.
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(Formatter())
        root_logger.addHandler(file_handler)

    if stream:
        stream_handler = logging.StreamHandler(stream)
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger.addHandler(stream_handler)

    if not filename and not stream:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger.addHandler(stream_handler)
