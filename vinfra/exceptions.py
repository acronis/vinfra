class VinfraError(Exception):
    pass


class TimeoutError(VinfraError):
    pass


class TaskError(VinfraError):
    def __init__(self, message, request_id=None):
        super(TaskError, self).__init__(message)
        self.request_id = request_id


class PollTimeoutError(TimeoutError):
    def __init__(self, message, last_result):
        super(PollTimeoutError, self).__init__(message)
        self.last_result = last_result


class UnknownApiVersion(VinfraError):
    pass
