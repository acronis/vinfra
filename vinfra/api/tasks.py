import logging
import time

from vinfra import exceptions
from vinfra.api import base


LOG = logging.getLogger(__name__)


class Task(base.Resource):
    ID_ATTR = 'task_id'

    def __init__(self, manager, info):
        # Uniform task because API returns different format for fail/success
        info['details'] = info.pop('error', None)
        if 'result' not in info:
            info['result'] = None
        super(Task, self).__init__(manager, info)

    def wait(self, **kwargs):
        return self.manager.wait(self, **kwargs)


class TaskManager(base.Manager):
    resource_class = Task
    default_timeout = 600

    def list(self):
        return self._list("/tasks")

    def get(self, task, **kwargs):
        url = "/tasks/{}".format(base.get_id(task))
        return self._get(url, **kwargs)

    # pylint: disable=no-member
    def wait(self, task, timeout=None, request_id=None, **kwargs):
        wait_timeout = timeout or self.default_timeout
        stime = time.time()
        while time.time() - stime < wait_timeout:
            task = self.get(task, request_id=request_id, **kwargs)
            if task.state in ('running', 'scheduled', 'cancelling'):
                time.sleep(1)
                continue

            if task.state == 'failed':
                details = task.details or "internal error"
                message = "Task {} failed. {}".format(task.task_id, details)
                raise exceptions.TaskError(message, request_id=request_id)

            if task.state not in ('aborted', 'cancelled', 'failed', 'success'):
                message = "Unknown task {} state '{}'".format(task.task_id,
                                                              task.state)
                raise exceptions.TaskError(message, request_id=request_id)

            # Even task is success its subtasks can fail
            if isinstance(task.result, dict) and task.result.get('errors'):
                errors = [err['message'] for err in task.result['errors']]
                message = "Task {} failed. {}".format(task.task_id,
                                                      ', '.join(errors))
                raise exceptions.TaskError(message, request_id=request_id)

            return task

        seconds = "second{}".format('' if wait_timeout == 1 else 's')
        message = ("Task {} waiting exceeded {} {} timeout"
                   .format(base.get_id(task), wait_timeout, seconds))
        raise exceptions.TimeoutError(message)
