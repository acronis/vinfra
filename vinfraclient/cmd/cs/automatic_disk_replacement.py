from vinfraclient.cmd.base import ShowOne


class ShowSettings(ShowOne):
    _description = 'Show automatic disk replacement settings.'

    def do_action(self, parsed_args):
        return self.app.vinfra.automatic_disk_replacement.settings.show_params()


class ChangeSettings(ShowOne):
    _description = 'Change automatic disk replacement settings.'

    __known_tiers = 0, 1, 2, 3
    __on, __off = 'on', 'off'

    def configure_parser(self, parser):
        for tier in self.__known_tiers:
            parser.add_argument(
                '--tier%d' % tier,
                choices=(self.__on, self.__off),
                default=None,
                help='Enable or disable automatic disk replacement for tier %d' % tier,
            )

    def do_action(self, parsed_args):
        kwargs = {}
        for tier in self.__known_tiers:
            val = getattr(parsed_args, 'tier%d' % tier)
            if val is None:
                continue
            kwargs['tier%d' % tier] = val.lower() == self.__on.lower()

        return self.app.vinfra.automatic_disk_replacement.settings.change_params(**kwargs)
