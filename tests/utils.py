import unittest

import mock
from cliff import columns as cliff_columns
from six.moves import StringIO


class FakeApp(object):
    def __init__(self):
        pass


class FakeResource(object):
    ID_ATTR = 'id'
    NAME_ATTR = 'name'

    def __init__(self, manager=None, info=None):
        info = info or {}
        self.manager = manager
        self._info = info
        for k, v in info.items():
            setattr(self, k, v)

    @classmethod
    def get_display_name(cls):
        return 'fake resource'

    def to_dict(self):
        return self._info


class ParserException(Exception):
    pass


class TestCommand(unittest.TestCase):
    def setUp(self):
        super(TestCommand, self).setUp()
        self.app = FakeApp()
        self.app.vinfra = mock.Mock()
        self.app.vinfra.alerts = mock.Mock()
        self.app.vinfra.alerts.resource_class = FakeResource

    def check_parser(self, cmd, args, verify_args):
        cmd_parser = cmd.get_parser('check_parser')

        with mock.patch('sys.stderr', new_callable=StringIO) as stderr_mock:
            try:
                parsed_args = cmd_parser.parse_args(args)
            except SystemExit:
                stderr_mock.seek(0)
                raise ParserException("Argument parse failed: {}"
                                      .format(stderr_mock.read()))
        for av in verify_args:
            orig_long_message = self.longMessage
            self.longMessage = True  # pylint: disable=invalid-name
            attr, value = av
            if attr:
                self.assertIn(attr, parsed_args)
                self.assertEqual(value, getattr(parsed_args, attr),
                                 "Parsed {!r} argument has wrong value".format(attr))
            self.longMessage = orig_long_message
        return parsed_args

    def assertListItemEqual(self, expected, actual):  # pylint: disable=invalid-name
        self.assertEqual(len(expected), len(actual))
        for item_expected, item_actual in zip(expected, actual):
            self.assertItemEqual(item_expected, item_actual)

    def assertItemEqual(self, expected, actual):  # pylint: disable=invalid-name
        self.assertEqual(len(expected), len(actual))
        for col_expected, col_actual in zip(expected, actual):
            if isinstance(col_expected, cliff_columns.FormattableColumn):
                self.assertIsInstance(col_actual, col_expected.__class__)
                self.assertEqual(col_expected.human_readable(),
                                 col_actual.human_readable())
            elif isinstance(col_actual, cliff_columns.FormattableColumn):
                self.assertEqual(col_expected, col_actual.machine_readable())
            else:
                self.assertEqual(col_expected, col_actual)
