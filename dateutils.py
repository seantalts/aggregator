from datetime import datetime
from dateutil.relativedelta import relativedelta


DURATIONS=["year", "month", "day", "hour", "minute"]


def _relevant_durations(duration):
    #it's important to use all the parts of a date larger than the target duration
    #in order to identify the duration uniquely
    return DURATIONS[:DURATIONS.index(duration) + 1]


def construct_relevant_date(dt, duration):
    args = [getattr(dt, d) for d in _relevant_durations(duration)]
    args += [1] * (3 - len(args))
    return datetime(*args)


def date_iterator(start, end, duration):
    start =  construct_relevant_date(start, duration) # zero out irrelevant parts
    end = construct_relevant_date(end, duration)
    curr = start
    delta = relativedelta(**{duration + "s": 1})
    yield curr
    while curr < end:
        curr += delta
        yield curr
