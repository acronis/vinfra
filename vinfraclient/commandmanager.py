import sys

import pkg_resources
from cliff import commandmanager as cliff_commandmanager
from stevedore import ExtensionManager

from vinfraclient.cmd.help import HelpCommand


class CommandManager(cliff_commandmanager.CommandManager):
    def __init__(self, dist):
        self.dist = dist
        self.plugins = []
        super(CommandManager, self).__init__('xxx')  # we don't need namespace

    def load_commands(self, namespace):
        # Do not use pkg_resources.iter_entry_points because it reads
        # entry_points.txt for each package in the system and takes time.
        self._add_self_commands()
        self._add_plugin_commands()

    def _add_self_commands(self):
        self_dist = pkg_resources.get_distribution('vinfraclient')
        for group, entries in self_dist.get_entry_map().items():
            # cache entrypoints to make it working faster in
            # stevedore.ExtensionManager
            ExtensionManager.ENTRY_POINT_CACHE[group] = entries.values()
        self._add_commands(self_dist)

    def _add_commands(self, dist):
        for entry_point in dist.get_entry_map('vinfra.cli').values():
            cmd_name = entry_point.name.replace('_', ' ')
            if cmd_name in self.commands:
                raise Exception("Command name duplicate: %s" % cmd_name)
            self.commands[cmd_name] = entry_point

    def _add_plugin_commands(self):
        for dist in pkg_resources.working_set:  # pylint: disable=not-an-iterable
            project_name = dist.project_name.replace('_', '-')
            if not project_name.startswith('vinfraclient-'):
                continue

            has_errors = False
            for ep in dist.get_entry_map('vinfra.cli.extenstion').values():
                try:
                    __import__(ep.module_name)
                except Exception as err:
                    sys.stderr.write('Failed to import plugin %r: %s'
                                     % (ep.name, err))
                    has_errors = True
                    break

                module = sys.modules[ep.module_name]
                self.plugins.append(module)

            if not has_errors:
                self._add_commands(dist)

    def __iter__(self):
        dist = pkg_resources.get_distribution('vinfraclient')
        hidden = {
            entry_point.name.replace('_', ' ')
            for entry_point in dist.get_entry_map('vinfra.cli.hidden').values()}
        return iter(cmd for cmd in self.commands.items()
                    if cmd[0] not in hidden)

    def add_command(self, name, command_class):
        if name == 'complete':
            return
        if name == 'help':
            super(CommandManager, self).add_command(name, HelpCommand)
            return
        super(CommandManager, self).add_command(name, command_class)

    def init_plugins(self, vinfra):
        for plugin in self.plugins:
            client = plugin.make_client(vinfra)
            setattr(vinfra, plugin.CLIENT_NAME, client)
