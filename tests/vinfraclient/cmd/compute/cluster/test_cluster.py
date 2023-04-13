from copy import deepcopy
import mock
from vinfraclient.cmd.compute.cluster import BaselineCPU
from tests import utils

baseline_cpu_info = [
    {
        u'models': [
            u'SandyBridge',
            u'Haswell',
        ],
        u'patched': True,
        u'node_id': u'id-0',
        u'hostname': u'master.vstoragedomain'
    },
    {
        u'models': [
            u'Haswell',
            u'Broadwell',
        ],
        u'patched': True,
        u'node_id': u'id-1',
        u'hostname': u've0.vstoragedomain'
    },
    {
        u'models': [
            u'Haswell',
            u'Broadwell',
            u'IvyBridge'
        ],
        u'patched': True,
        u'node_id': u'id-2',
        u'hostname': u've1.vstoragedomain'
    }
]


class FakeNode(object):
    def __init__(self, info):
        self.node_id = info['node_id']
        self.host = info['hostname']
        self.NAME_ATTR = 'host'  # pylint: disable=invalid-name
        self.ID_ATTR = 'node_id'  # pylint: disable=invalid-name


class TestBaselineCPU(utils.TestCommand):
    def setUp(self):
        super(TestBaselineCPU, self).setUp()
        self.cmd = BaselineCPU(self.app, None)

    def test_common_baseline(self):
        self.app.vinfra.compute.cluster.info = mock.Mock(return_value=baseline_cpu_info)
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        _columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(data[0].machine_readable(),
                         {'models': [u'Haswell'], 'patched': True})

    def test_all_nodes_patched(self):
        new_info = deepcopy(baseline_cpu_info)
        new_info[0]['patched'] = False
        self.app.vinfra.compute.cluster.info = mock.Mock(return_value=new_info)
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        _columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(data[0].machine_readable(),
                         {'models': [u'Haswell'], 'patched': False})

    def test_selecting_nodes(self):
        self.app.vinfra.compute.cluster.info = mock.Mock(return_value=baseline_cpu_info)
        nodes = [FakeNode(info) for info in baseline_cpu_info]
        self.app.vinfra.nodes.list = mock.Mock(return_value=nodes)
        arglist = ['--nodes', 've0.vstoragedomain,ve1.vstoragedomain']
        verifylist = [
            ('nodes', ['ve0.vstoragedomain', 've1.vstoragedomain'])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        _columns, data = self.cmd.take_action(parsed_args)
        self.assertSetEqual(set(data[0].machine_readable()['models']),
                            {u'Broadwell', u'Haswell'})
