import argparse
import datetime
import uuid

import progressbar as pb

from vinfra.exceptions import TaskError

from vinfraclient.cmd.base import Lister, ShowOne
from vinfraclient.exceptions import CommandError
from vinfraclient.formatters import columns as fmt_columns
from vinfraclient.utils import progress_bar_context


def cut_task(task):
    res = dict(task)
    fields = ['task_id', 'name', 'state', 'details', 'result', 'progress']
    for key in task.keys():
        if key in fields:
            continue
        res.pop(key)
    return res


def task_id_type(value):
    # Curious bug when we are getting exploding a brain issue
    # #VSTOR-45664 if value='?'. Let's validate value is uuid.
    try:
        uuid.UUID(value)
    except Exception:
        raise argparse.ArgumentTypeError('invalid task ID format')
    return value


class TracebackColumn(fmt_columns.BaseColumn):
    def human_readable(self, value=None):
        if self._value is not None:
            return '\n'.join([line.strip() for line in self._value])
        return super(TracebackColumn, self).human_readable()


class ListTask(Lister):
    _description = "List tasks"
    _default_fields = ['task_id', 'state', 'name']

    def do_action(self, parsed_args):
        tasks = self.app.vinfra.tasks.list()
        return tasks


class ShowTask(ShowOne):
    _description = "Show task details."
    _formatters = {'traceback': TracebackColumn}

    def configure_parser(self, parser):
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Show all task fields (for debug only)."
        )
        parser.add_argument(
            "task",
            metavar="<task>",
            type=task_id_type,
            help="Task ID"
        )

    def do_action(self, parsed_args):
        task = self.app.vinfra.tasks.get(parsed_args.task)
        task = task.to_dict()
        if not parsed_args.debug:
            return cut_task(task)
        return task


class WaitTask(ShowOne):
    _description = "Wait for the task to complete."

    def configure_parser(self, parser):
        parser.add_argument(
            "task",
            metavar="<task_id>",
            type=task_id_type,
            help="Task ID"
        )
        parser.add_argument(
            "--timeout",
            metavar="<seconds>",
            type=int,
            default=600,
            help="A timeout for the task to complete, in seconds (default: 600)"
        )

    @staticmethod
    def task_wait(task, timeout):
        try:
            return task.wait(timeout=timeout)
        except TaskError as err:
            raise CommandError(err)

    def do_action(self, parsed_args):
        timeout = parsed_args.timeout
        formatter = parsed_args.formatter

        task = self.app.vinfra.tasks.get(parsed_args.task)

        if formatter == 'table':
            self.app.print_message("Task '%s' waiting ...", task.task_id)

            timeout_str = datetime.timedelta(seconds=timeout)
            pattern = '[timeout: {}, elapsed time: %s]  '.format(timeout_str)
            widgets = [pb.Timer(format=pattern), pb.AnimatedMarker()]

            pbar = pb.ProgressBar(maxval=80, term_width=80, widgets=widgets,
                                  fd=self.app.stderr)
            with progress_bar_context(self.app, pbar, timeout=timeout):
                task = self.task_wait(task, timeout)
        else:
            task = self.task_wait(task, timeout)

        return cut_task(task.to_dict())
