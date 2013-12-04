"""Field module for specifying fields to aggregate"""
from collections import namedtuple
from datetime import timedelta, datetime


Key = namedtuple("Stat", ['target', 'owner', 'duration', 'time'])
DURATIONS=["year", "month", "day", "hour", "minute"]
TYPES=("follow", "favorite", "order")


def _relevant_durations(duration):
    #it's important to use all the parts of a date larger than the target duration
    #in order to identify the duration uniquely
    return DURATIONS[:DURATIONS.index(duration) + 1]


def _construct_relevant_date(dt, duration):
    return datetime(*(getattr(dt, d) for d in _relevant_durations(duration)))


def date_iterator(start, end, duration):
    start =  _construct_relevant_date(start, duration) # zero out irrelevant parts
    end = _construct_relevant_date(end, duration)
    curr = start
    delta = timedelta(**{duration + "s": 1})
    while curr < end:
        yield curr
        curr += delta


def _count_type(t):
    def _dict_count(d):
        if d['type'] == t:  #Assuming there is always a type?
            return 1
        else:
            return 0
    return _dict_count


class Field(object):

    TARGET_FINDERS={t: _count_type(t) for t in TYPES}
    TARGET_FINDERS["total"] = lambda d: d['total'] if 'total' in d else 0
    #Add more finders here when needed


    def __init__(self, field_string):
        parts = field_string.split("/")
        assert len(parts) == 2 or len(parts) == 3, "Fields must have 2 or 3 parts."
        self.target = parts[0]
        if len(parts) == 2:  # no duration
            self.duration = None
            self.owner = parts[1]
        else:
            self.duration = parts[1]
            assert self.duration in DURATIONS, "Duration must be one of %s" % (
                DURATIONS,)
            self.owner = parts[2]

        self.value = self.TARGET_FINDERS[self.target]
        if self.duration:
            self.durations = _relevant_durations(self.duration)

    @staticmethod
    def _get_time(dict_, duration):
        dt = dict_['time']
        return getattr(dt, duration)

    def _find_time(self, d):
        if not self.duration:
            return "all time"
        return _construct_relevant_date(d['time'], self.duration)

    def _find_owner(self, d):
        return self.owner + ": " + str(d[self.owner])

    def key(self, d):
        return Key(self.target, self._find_owner(d), self.duration, self._find_time(d))

    def __str__(self):
        return "Field(%s, %s, %s)" % (self.target, self.duration, self.owner)

    __repr__ = __str__


def test_target_finder():
    follow_finder = Field.TARGET_FINDERS["follow"]
    assert follow_finder({"type": "follow"}) == 1
    assert follow_finder({"type": "favorite"}) == 0

