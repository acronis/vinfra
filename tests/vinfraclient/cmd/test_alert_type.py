from tests import utils
from vinfraclient.cmd import alert_type


def _create_one_alert_type(attrs=None):
    attrs = attrs or {}
    info = {
        'type': 'test_alert_type',
        'group': 'test_group',
    }
    info.update(attrs)
    return utils.FakeResource(info=info)


def _create_alert_types(count):
    return [
        _create_one_alert_type({'type': 'test_alert_type_{}'.format(num)}) for num in range(count)
    ]


class TestAlertType(utils.TestCommand):
    def setUp(self):
        super(TestAlertType, self).setUp()
        self.alert_types_mock = self.app.vinfra.alert_types

    @staticmethod
    def _get_common_cols_data(alert_type):
        columns = (
            'type',
            'group'
        )
        data = (
            alert_type.type,
            alert_type.group
        )
        return columns, data


class TestListAlertType(TestAlertType):
    _alert_types = _create_alert_types(3)
    columns = (
        'type',
        'group'
    )
    data = []
    for alert_type in _alert_types:
        data.append((
            alert_type.type,
            alert_type.group
        ))

    def setUp(self):
        super(TestListAlertType, self).setUp()
        self.cmd = alert_type.ListAlertType(self.app, None)
        self.alert_types_mock.list.return_value = self._alert_types

    def test_alert_list(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(columns, self.columns)
        self.assertListItemEqual(self.data, list(data))
