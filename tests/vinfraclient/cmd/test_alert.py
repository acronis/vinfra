import mock

from tests import utils
from vinfraclient import exceptions
from vinfraclient.cmd import alert
from vinfraclient.formatters import columns as fmt_columns

# Instance of 'FakeResource' has no 'id' member (no-member)
# pylint: disable=no-member

def _create_one_alert(attrs=None):
    attrs = attrs or {}
    info = {
        'id': 0,
        'type': 'Test alert type',
        'datetime': '2020-10-02T15:10:11.842410+00:00',
        'severity': 'error',
        'enabled': True,
        # Put only some extra columns as it doesn't affect the logic
        'cluster_name': 'test_cluster',
        'host': 'test_host',
    }
    info.update(attrs)
    return utils.FakeResource(info=info)


def _create_alterts(count):
    return [_create_one_alert({'id': idx}) for idx in range(count)]


class TestAlert(utils.TestCommand):
    def setUp(self):
        super(TestAlert, self).setUp()
        # Get a shortcut to the alert client
        self.alerts_mock = self.app.vinfra.alerts

    @staticmethod
    def _get_common_cols_data(alert):
        # in alphabet order
        columns = (
            'cluster_name',
            'datetime',
            'enabled',
            'host',
            'id',
            'severity',
            'type'
        )
        data = (
            alert.cluster_name,
            fmt_columns.DatetimeColumn(alert.datetime),
            alert.enabled,
            alert.host,
            alert.id,
            alert.severity,
            alert.type,
        )
        return columns, data


class TestListAlert(TestAlert):
    _alerts = _create_alterts(count=3)

    columns = (
        'id',
        'type',
        'datetime',
        'severity',
        'enabled',
    )
    columns_long = (
        'id',
        'type',
        'datetime',
        'severity',
        'enabled',
        # Put only some extra columns as it doesn't affect the logic
        'cluster_name',
        'host',
    )

    data = []
    for alert in _alerts:
        data.append((
            alert.id,
            alert.type,
            fmt_columns.DatetimeColumn(alert.datetime),
            alert.severity,
            alert.enabled,
        ))

    data_long = []
    for alert in _alerts:
        data_long.append((
            alert.id,
            alert.type,
            fmt_columns.DatetimeColumn(alert.datetime),
            alert.severity,
            alert.enabled,
            alert.cluster_name,
            alert.host,
        ))

    def setUp(self):
        super(TestListAlert, self).setUp()

        # Get the command object to test
        self.cmd = alert.ListAlert(self.app, None)
        self.alerts_mock.list.return_value = self._alerts

    def test_alert_list_no_option(self):
        arglist = []
        verifylist = [
            ('all', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(columns, self.columns)
        self.assertListItemEqual(self.data, list(data))

    def test_alert_list_long(self):
        arglist = ['--long']
        verifylist = [
            ('all', False),
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.alerts_mock.list.assert_called_once_with(enabled=True, lang='en')
        self.assertEqual(columns, self.columns_long)
        self.assertListItemEqual(self.data_long, list(data))

    def test_alert_list_all(self):
        arglist = ['--all']
        verifylist = [
            ('all', True),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.alerts_mock.list.assert_called_once_with(enabled=False, lang='en')
        self.assertEqual(columns, self.columns)
        self.assertListItemEqual(self.data, list(data))


class TestShowAlert(TestAlert):
    _alert = _create_one_alert()
    columns, data = TestAlert._get_common_cols_data(_alert)

    def setUp(self):
        super(TestShowAlert, self).setUp()

        # Get the command object to test
        self.cmd = alert.ShowAlert(self.app, None)
        self.alerts_mock.list.return_value = [self._alert]

    def test_alert_show_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(utils.ParserException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_show_alert(self):
        arglist = [
            str(self._alert.id),
        ]
        verifylist = [
            ('alert', self._alert.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.alerts_mock.list.assert_called_once_with()

        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)

    def test_show_alert_wrong_id(self):
        arglist = [
            'wrong_id',
        ]
        verifylist = []
        self.assertRaises(utils.ParserException,
                          self.check_parser, self.cmd, arglist, verifylist)

    def test_show_alert_unexist(self):
        arglist = [
            '123',
        ]
        verifylist = [
            ('alert', 123)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as err:
            self.assertEqual(
                "No fake resource with a name or ID of '123' exists.", str(err))

class TestDeleteAlert(TestAlert):
    _alert = _create_one_alert()
    _alert_disabled = _create_one_alert({
        'id': _alert.id,
        'enabled': False
    })
    _alert.update = mock.Mock(return_value=_alert_disabled)
    columns, data = TestAlert._get_common_cols_data(_alert_disabled)

    def setUp(self):
        super(TestDeleteAlert, self).setUp()

        # Get the command object to test
        self.cmd = alert.DeleteAlert(self.app, None)
        self.alerts_mock.list.return_value = [self._alert]

    def test_alert_delete(self):
        arglist = [
            str(self._alert.id),
        ]
        verifylist = [
            ('alert', self._alert.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        # List is calld by utils.find_resource:
        self.alerts_mock.list.assert_called_once_with()
        self._alert.update.assert_called_once_with(enabled=False)
        self.assertItemEqual(self.data, data)
