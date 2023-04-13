class VinfraError(Exception):
    """Common exception type."""
    pass


class ValidationError(VinfraError):
    """Command params validation error."""
    pass


class CommandError(VinfraError):
    """Error in commands."""
    pass


class AbortError(VinfraError):
    """Error in the middle of command performing."""
    pass
