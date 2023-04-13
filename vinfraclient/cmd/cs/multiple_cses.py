import argparse

from vinfraclient.cmd.base import ShowOne


class ShowSettings(ShowOne):
    _description = 'Show NVMe performance settings.'

    def do_action(self, parsed_args):
        return self.app.vinfra.multiple_cses.settings.show_params()


class ChangeSettings(ShowOne):
    _description = 'Enabling/Disabling NVMe performance.'

    __known_tiers = 0, 1, 2, 3

    @classmethod
    def number_of_cses_per_disk(cls, number):
        try:
            number = int(number)
        except ValueError:
            raise argparse.ArgumentTypeError('1 or more CSes per disk must be specified')

        if number < 1:
            raise argparse.ArgumentTypeError("Minimum number of CSes per disk is 1")

        return number

    def configure_parser(self, parser):
        for tier in self.__known_tiers:
            parser.add_argument(
                '--tier%d' % tier,
                type=self.number_of_cses_per_disk,
                metavar='number',
                default=None,
                help='Set number of CSes per disk for tier %d' % tier,
            )

    def do_action(self, parsed_args):
        kwargs = {}
        for tier in self.__known_tiers:
            number = getattr(parsed_args, 'tier%d' % tier)
            if number is None:
                continue
            kwargs['tier%d' % tier] = number

        return self.app.vinfra.multiple_cses.settings.change_params(**kwargs)
