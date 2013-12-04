"""Field module for specifying fields to aggregate"""
import itertools

def _count_type(t):
    def _dict_count(d):
        if d['type'] == t:  #Assuming there is always a type?
            return 1
        else:
            return 0
    return _dict_count


class Field(object):
    TYPES=("follow", "favorite", "order")
    TARGET_FINDERS={t: _count_type(t) for t in TYPES}
    TARGET_FINDERS["total"] = lambda d: d['total'] if 'total' in d else 0
    DURATIONS=["year", "month", "day", "hour", "minute"]

    def __init__(self, field_string):
        parts = field_string.split("/")
        assert len(parts) == 2 or len(parts) == 3, "Fields must have 2 or 3 parts."
        self.target = parts[0]
        if len(parts) == 2:  # no duration
            self.duration = None
            self.owner = parts[1]
        else:
            self.duration = parts[1]
            assert self.duration in self.DURATIONS, "Duration must be one of %s" % (
                self.DURATIONS,)
            self.owner = parts[2]

        self.value = self.TARGET_FINDERS[self.target]
        if self.duration:
            self.durations = self.DURATIONS[:self.DURATIONS.index(self.duration) + 1]

    @staticmethod
    def _get_duration(dict_, duration):
        dt = dict_['time']
        return str(getattr(dt, duration))

    def _find_duration(self, d):
        if not self.duration:
            return "all time"
        return ".".join(self._get_duration(d, duration) for duration in self.durations)

    def _find_owner(self, d):
        return self.owner + ": " + str(d[self.owner])

    def key(self, d):
        return (self.target, self._find_duration(d), self._find_owner(d))

    def __str__(self):
        return "Field(%s, %s, %s)" % (self.target, self.duration, self.owner)

    __repr__ = __str__


def test_target_finder():
    follow_finder = Field.TARGET_FINDERS["follow"]
    assert follow_finder({"type": "follow"}) == 1
    assert follow_finder({"type": "favorite"}) == 0

