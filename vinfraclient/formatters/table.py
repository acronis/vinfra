from argparse import ArgumentParser

from cliff.formatters import table as cliff_table


class TableFormatter(cliff_table.TableFormatter):
    def add_argument_group(self, parser):
        group = parser.add_argument_group('table formatter')
        group.add_argument(
            '--max-value-length',
            type=int,
            default=80,
            help=('Maximum value length. Longer values will be truncated. '
                  'Set this option to -1 to turn off value truncation. '
                  'The default is 80.')
        )

    def _fix_parsed_args(self, parsed_args):
        # Trick to make cliff argparse namespace happy
        parser = ArgumentParser()
        super(TableFormatter, self).add_argument_group(parser)
        cliff_parsed_args = parser.parse_args(['--print-empty'])
        parsed_args.__dict__.update(cliff_parsed_args.__dict__)

    def emit_list(self, column_names, data, stdout, parsed_args):
        self._fix_parsed_args(parsed_args)
        super(TableFormatter, self).emit_list(
            column_names, data, stdout, parsed_args)

    def emit_one(self, column_names, data, stdout, parsed_args):
        self._fix_parsed_args(parsed_args)
        super(TableFormatter, self).emit_one(
            column_names, data, stdout, parsed_args)
