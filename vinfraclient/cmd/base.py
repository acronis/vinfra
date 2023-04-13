import argparse
import json
import inspect
import logging
import string
import uuid

import abc
import datetime
import os
import progressbar as pb
import yaml
from yaml.representer import SafeRepresenter
from cliff import command as cliff_command
from cliff import lister as cliff_lister
from cliff import show as cliff_show
from requests import exceptions as request_exceptions

from vinfra import exceptions as vinfra_exceptions
from vinfra.api import base as vinfra_base
from vinfraclient import exceptions
from vinfraclient import utils
from vinfraclient.argtypes import parse_dict_options
from vinfraclient.formatters import columns as fmt_columns

HTTP_ERROR = 1
COMMAND_ERROR = 2
CONNECTION_ERROR = 101
TIMEOUT_ERROR = 102

LOG = logging.getLogger(__name__)


def represent_uuid(inst, data):
    return inst.represent_str(str(data))


SafeRepresenter.add_representer(uuid.UUID, represent_uuid)


def flatten_args(parsed_args, arg_name_list):
    res = {}
    for arg_name in arg_name_list:
        arg_value = getattr(parsed_args, arg_name)
        if arg_value is not None:
            res[arg_name] = arg_value
    return res


class FilterAction(argparse.Action):
    def __init__(self, *args, **kwargs):
        operators = kwargs.pop('operators', [])
        super(FilterAction, self).__init__(*args, **kwargs)

        if not isinstance(operators, (tuple, list)):
            operators = [operators]
        self._operators = operators

        help_message = kwargs.get('help', '').strip()
        if help_message:
            if not help_message.endswith('.'):
                help_message += '. '
            if not help_message.endswith(' '):
                help_message += ' '
        if len(self._operators) > 1:
            help_message += ('Supported filter operators: {}'
                             .format(', '.join(self._operators)))
        else:
            help_message += ('Supported filter operator: {}'
                             .format(', '.join(self._operators)))
        help_message += ('. The filter format is '
                         '<operator>:<value1>[,<value2>,...].')
        self.help = help_message

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class HelpFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        lines = []
        for line in text.splitlines():
            res = super(HelpFormatter, self)._split_lines(line, width)
            lines.extend(res)
        return lines


class _ErrorFormatter(string.Formatter):
    def get_value(self, key, args, kwargs):
        if isinstance(key, str):
            value = kwargs.get(key, '')
            if value is None:
                value = ''
            return value
        return super(_ErrorFormatter, self).get_value(key, args, kwargs)


class Command(cliff_command.Command):
    client_required = True
    auth_required = True
    deprecated_reason = None

    def __init__(self, app, app_args, cmd_name=None):
        # NOTE(akurbatov): cmd_name is needed only to load command hooks
        # loading commands hooks is too slow operatiob because it uses
        # pkg_resources.iter_entry_points(). Do not pass cmd_name to make
        # command loading faster.
        super(Command, self).__init__(app, app_args)
        self._cmd_name = cmd_name

    def get_parser(self, prog_name):
        parser = super(Command, self).get_parser(prog_name)
        parser.formatter_class = HelpFormatter
        parser.register('action', 'filter', FilterAction)

        self._configure_parser_inner(parser)
        return parser

    def _configure_parser_inner(self, parser):
        self.configure_parser(parser)

    def configure_parser(self, parser):
        """Add a command specific options here."""
        pass

    def run(self, parsed_args):
        if self.deprecated:
            message = ("The command '{}' is deprecated and will be removed in "
                       "the future.".format(self._cmd_name))
            if self.deprecated_reason:
                message += " " + self.deprecated_reason
            self.app.stderr.write(message + '\n')
        try:
            result = super(Command, self).run(parsed_args)
        except Exception as err:
            retcode = self.handle_exception(err)
            if retcode:
                return retcode
            raise

        if result:
            self.app.stderr.write("Operation failed (ret={})\n".format(result))

        return result

    def handle_exception(self, err):
        if isinstance(err, request_exceptions.HTTPError):
            message, stderr = self._get_http_error(err)
            self._produce_error(message, stderr=stderr)
            return HTTP_ERROR

        elif isinstance(err, exceptions.ValidationError):
            self._produce_error("command error: %s" % err)
            return COMMAND_ERROR

        elif isinstance(err, (exceptions.VinfraError,
                              vinfra_exceptions.VinfraError,
                              UnicodeEncodeError,
                              UnicodeDecodeError)):
            message = "command failed: {}".format(err)
            request_id = getattr(err, 'request_id', None)
            if request_id:
                message = '{} (Request-ID: {})'.format(message, request_id)
            self._produce_error(message)
            return COMMAND_ERROR

        elif isinstance(err, request_exceptions.ConnectionError):
            self._produce_error("connection error: %s" % err)
            return CONNECTION_ERROR

        elif isinstance(err, vinfra_exceptions.TimeoutError):
            self._produce_error("command timeouted: %s" % err)
            return TIMEOUT_ERROR

        elif isinstance(err, request_exceptions.Timeout):
            self._produce_error("timeout error: %s" % err)
            return TIMEOUT_ERROR

        return None

    def _get_http_error(self, err):
        stderr = True
        error_params = self._get_http_error_params(err)

        if os.environ.get('VINFRA_RAW_HTTP_ERROR'):
            message = json.dumps(error_params)
        elif os.environ.get('VINFRA_ERROR_FORMAT'):
            stderr = False
            message = _ErrorFormatter().format(
                os.environ['VINFRA_ERROR_FORMAT'], **error_params)
        else:
            reason = error_params['reason']
            message = error_params['message']
            request_id = error_params['request_id']

            message = '{} ({})'.format(message, reason)
            if request_id:
                message = '{} (Request-ID: {})'.format(message, request_id)
        return message, stderr

    def _get_http_error_params(self, err):
        response = err.response

        if isinstance(response.reason, bytes):
            reason = response.reason.decode('utf-8', 'ignore')
        else:
            reason = response.reason

        try:
            body = response.json()
        except ValueError:
            error_dict = {}
        else:
            if isinstance(body, dict):
                error_dict = body.get("error")
                # raising werkzeug.exceptions.HTTPException
                # on the backend side with message field:
                if not error_dict and "message" in body:
                    error_dict = {"message": body["message"]}
            else:
                error_dict = {"message": unicode(body)}

        error_dict = error_dict or {}

        http_error_params = {
            "url": response.url,
            "http_code": response.status_code,
            "http_reason": reason,
            "request_id": response.headers.get('x-request-id'),
            # next error params are deprecated
            # and will be removed in the future:
            "status_code": response.status_code,
            "reason": reason,
            "error": error_dict,
        }
        message = self._extract_error_message(error_dict)
        if not message:
            message = str(err)
        http_error_params['message'] = message

        return http_error_params

    @staticmethod
    def _extract_error_message(error_dict):
        message = error_dict.get('message')
        errors = error_dict.get('errors')
        fields = error_dict.get('fields')

        if message:
            return message
        elif errors:
            error = errors[0] or {}
            return error.get('message')
        elif fields:
            errors = []
            for key, value in fields.items():
                key = 'invalid "%s" value' % key
                errors.append({key: value})
            message = yaml.safe_dump(errors, default_flow_style=False)
            return message
        # cannot find error message in the response
        return None

    def _produce_error(self, error_details, stderr=True):
        message = error_details.rstrip('\n')
        stream = self.app.stderr if stderr else self.app.stdout
        stream.write(message + '\n')

    def take_action(self, parsed_args):
        return_code = self.do_action(parsed_args)
        if not return_code:  # success
            self.app.print_message("Operation successful.")
        return return_code

    def do_action(self, parsed_args):
        """Do a command action."""


class DisplayMixin(object):
    _formatters = {}

    def _formattable_entity(self, parsed_args, data):
        if not data:
            return {}

        if not isinstance(data, dict):
            data = data.to_dict()
            for key in data.keys():
                if key.endswith("_manager"):
                    del data[key]

        rv = {}
        for key in data.keys():
            formatter = self._formatters.get(key, fmt_columns.BaseColumn)
            try:
                func_args = inspect.getargspec(formatter.__init__).args
            except TypeError:
                func_args = []

            kwargs = {'output_formatter': parsed_args.formatter}
            if 'max_length' in func_args:
                kwargs['max_length'] = parsed_args.max_value_length

            rv[key] = formatter(data[key], **kwargs)
        return rv

    def produce_output(self, parsed_args, column_names, data):
        # cliff raises ValueError if columns are not recognized.
        # Check it before and raise ValidationError instead.
        if parsed_args.columns:
            if not [c for c in column_names if c in parsed_args.columns]:
                raise exceptions.ValidationError(
                    "No recognized column names: {}".format(parsed_args.columns))

        return super(DisplayMixin, self).produce_output(
            parsed_args, column_names, data)


class Lister(Command, DisplayMixin, cliff_lister.Lister):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def _default_fields(self):
        """Default fields for listing."""

    @property
    def formatter_namespace(self):
        return 'vinfra.formatter.list'

    def _configure_parser_inner(self, parser):
        # sorting from cliff conflicts with sorting
        # on the backend side. Do not allow to sort yet.
        for action in parser._actions:  # pylint: disable=protected-access
            if action.dest == 'sort_columns':
                action.help = argparse.SUPPRESS
                break

        parser.add_argument(
            "--long",
            action="store_true",
            help="Enable access and listing of all fields of objects."
        )
        super(Lister, self)._configure_parser_inner(parser)

    def take_action(self, parsed_args):
        data = self.do_action(parsed_args)
        data = data if data else []

        columns = list(self._default_fields)
        all_columns = set()
        formattable_data = []
        for el in data:
            el = self._formattable_entity(parsed_args, el)
            formattable_data.append(el)
            all_columns.update(el.keys())

        if parsed_args.long:
            extra_columns = all_columns - set(columns)
            columns.extend(sorted(extra_columns))

        rows = [[el.get(key) for key in columns] for el in formattable_data]
        return tuple(columns), rows


class ShowOne(Command, DisplayMixin, cliff_show.ShowOne):
    @property
    def formatter_namespace(self):
        return 'vinfra.formatter.show'

    def take_action(self, parsed_args):
        data = self.do_action(parsed_args)
        data = self._formattable_entity(parsed_args, data)
        keys, values = self.dict2columns(data)
        return keys, values


class TaskCommand(ShowOne):
    _default_timeout = vinfra_base.Task.default_timeout

    def _configure_parser_inner(self, parser):
        task_group = parser.add_argument_group(
            title="command run options",
            description='additional command options',
        )
        task_group.add_argument(
            "--wait",
            action="store_true",
            help="Wait for the operation to complete (synchronous mode)."
        )
        task_group.add_argument(
            "--timeout",
            metavar="<seconds>",
            type=int,
            default=self._default_timeout,
            help="A timeout for the operation to complete if --wait is "
                 "specified, in seconds (default: %d)" % self._default_timeout
        )
        super(TaskCommand, self)._configure_parser_inner(parser)

    def task_wait(self, task, parsed_args):
        timeout = parsed_args.timeout
        formatter = parsed_args.formatter

        if formatter != 'table':
            return task.wait(timeout)

        if isinstance(task, vinfra_base.BackendTask):
            self.app.print_message("Task ID: %s", task.data['task_id'])

        timeout_str = datetime.timedelta(seconds=timeout)
        format_pattern = ('Operation waiting [timeout: {}, elapsed time: %s] '
                          ''.format(timeout_str))
        widgets = [pb.Timer(format=format_pattern), pb.AnimatedMarker()]

        pbar = pb.ProgressBar(maxval=80, term_width=80, widgets=widgets,
                              fd=self.app.stderr)
        with utils.progress_bar_context(self.app, pbar, timeout=timeout):
            return task.wait(timeout=timeout)

    def take_action(self, parsed_args):
        task = self.do_action(parsed_args)
        if not isinstance(task, vinfra_base.Task):
            raise ValueError("TaskCommand must return Task object")

        if parsed_args.wait:
            data = self.task_wait(task, parsed_args)
        else:
            data = task.get_info()

        data = self._formattable_entity(parsed_args, data)
        keys, values = self.dict2columns(data)
        if not keys and not parsed_args.wait:
            self.app.print_message("Operation accepted.")

        return keys, values


class SuppressMixin(object):
    # This hack tells cliff to suppress the command and do not show in the help message
    deprecated = True


class KeyValuePair(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        metadata_dict = getattr(namespace, self.dest, {}) or {}
        metadata = parse_dict_options(values)
        if len(metadata) > 1:
            raise argparse.ArgumentTypeError("Wrong key=value format")
        metadata_dict.update(metadata)
        setattr(namespace, self.dest, metadata_dict)
