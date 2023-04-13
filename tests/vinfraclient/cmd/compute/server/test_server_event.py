from tests import utils
from vinfraclient.cmd.compute import server


def _create_event(attrs=None, request_id=None, server_id=None):
    attrs = attrs or {}
    request_id = request_id or 'req-10000000-0000-0000-0000-000000000000'
    server_id = server_id or '10000000-0000-0000-0000-000000000000'
    info = dict(
        user_id='11000000-0000-0000-0000-000000000000',
        username='foo',
        start_time='2000-12-24T00:00:00.000000',
        request_id=request_id,
        action='suspend',
        project_id='11100000-0000-0000-0000-000000000000',
        status='Success',
        server_id=server_id
    )
    info.update(attrs)
    return utils.FakeResource(info=info)


def _create_events(event_count=1, server_id=None):
    return [
        _create_event(
            request_id='req-{0}0000000-0000-0000-0000-000000000000'.format(num),
            server_id=server_id or '10000000-0000-0000-0000-000000000000'
        ) for num in range(event_count)
    ]


def _get_common_cols_data(events, sort=False):
    columns = (
        'project_id',
        'server_id',
        'request_id',
        'action',
        'start_time',
        'user_id',
        'username',
        'status'
    )

    if sort:
        columns = tuple(
            sorted(columns)
        )

    data = [
        tuple(
            getattr(event, k) for k in columns
        ) for event in events
    ]
    return columns, data


class TestListServerEvent(utils.TestCommand):
    events = _create_events(3)
    columns, data = _get_common_cols_data(events)

    def setUp(self):
        super(TestListServerEvent, self).setUp()
        self.events_manager = \
            self.app.vinfra.compute.servers.get.return_value.events_manager
        self.events_manager.list.return_value = self.events
        self.cmd = server.EventList(self.app, None)

    def test_event_list(self):
        arglist = [
            '--server', '10000000-0000-0000-0000-000000000000'
        ]
        verifylist = [
            ('server', '10000000-0000-0000-0000-000000000000'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.data, data)


class TestShowServerEvent(utils.TestCommand):
    events = _create_events(1)
    columns, data = _get_common_cols_data(events, sort=True)

    def setUp(self):
        super(TestShowServerEvent, self).setUp()
        self.event_manager = \
            self.app.vinfra.compute.servers.get.return_value.events_manager
        self.event_manager.get.return_value = self.events[0]
        self.cmd = server.EventShow(self.app, None)

    def test_event_show(self):
        arglist = [
            '--server', '10000000-0000-0000-0000-000000000000',
            'req-10000000-0000-0000-0000-000000000000'
        ]
        verifylist = [
            ('server', '10000000-0000-0000-0000-000000000000'),
            ('event', 'req-10000000-0000-0000-0000-000000000000'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertListItemEqual(sorted(self.columns), sorted(columns))
        self.assertItemEqual(self.data[0], data)
