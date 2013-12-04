from functools import wraps


def and_then(f1, f2):
    """Returns a function that calls f2 on the result of f1."""
    @wraps(f1)
    def and_then_wrapper(*args, **kwargs):
        return f2(f1(*args, **kwargs))
    return and_then_wrapper

