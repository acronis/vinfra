from argparse import ArgumentParser

from cliff.formatters.json_format import JSONFormatter as _JsonFormatter


class JSONFormatter(_JsonFormatter):
    def add_argument_group(self, parser):
        pass

    @property
    def default_parsed_args(self):
        # Trick to get cliff default namespace
        parser = ArgumentParser()
        super(JSONFormatter, self).add_argument_group(parser)
        parsed_args = parser.parse_args([])
        return parsed_args

    def emit_list(self, column_names, data, stdout, parsed_args):
        super(JSONFormatter, self).emit_list(
            column_names, data, stdout, self.default_parsed_args)

    def emit_one(self, column_names, data, stdout, parsed_args):
        super(JSONFormatter, self).emit_one(
            column_names, data, stdout, self.default_parsed_args)
