from datetime import datetime
import yaml

from six import string_types
from cliff import columns


missing = object()


class BaseColumn(columns.FormattableColumn):
    def __init__(self, value, max_length=80, output_formatter=None):
        super(BaseColumn, self).__init__(value)
        self._max_length = max_length
        self._output_formatter = output_formatter

    def human_readable(self, value=None):  # pylint: disable=arguments-differ
        value = self._value if value is None else value
        if value is None:
            return ''

        if isinstance(value, (dict, list, tuple)):
            # Do not truncate nested objects
            return yaml.safe_dump(value, default_flow_style=False).strip()

        if isinstance(value, string_types):
            if self._max_length != -1 and len(value) > self._max_length:
                tr = '...<truncated>'
                return value[:max(self._max_length - len(tr), 0)] + tr

        return value

    def machine_readable(self, value=None):  # pylint: disable=arguments-differ
        value = self._value if value is None else value
        if self._output_formatter == 'value':
            return self.human_readable(value)

        return value


class DatetimeColumn(BaseColumn):
    def human_readable(self, value=None):
        dformat = '%Y-%m-%dT%H:%M:%S.%f+00:00'
        dtime = datetime.strptime(self._value, dformat)
        value = dtime.strftime('%Y-%m-%dT%H:%M:%S')
        return super(DatetimeColumn, self).human_readable(value=value)


class ListColumn(BaseColumn):
    def human_readable(self, value=None):
        if self._value is not None:
            value = ','.join(self._value)
        return super(ListColumn, self).human_readable(value=value)
