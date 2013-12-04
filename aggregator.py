from dateutils import date_iterator
from collections import defaultdict
from itertools import groupby
from datetime import datetime


class Aggregator(object):
    def __init__(self, fields):
        self.fields = fields
        self.stats = defaultdict(int)
        self.start_date = datetime(9999, 1, 1)
        self.end_date = datetime(1, 1, 1)

    def __str__(self):
        return "Aggregator(%s)" % (", ".join(map(str, self.fields)),)

    def add(self, d):
        for field in self.fields:
            val = field.value(d)
            if val:
                self.stats[field.key(d)] += val  #XXX use generic aggregator functions
                self.start_date = min(self.start_date, d['time'])
                self.end_date = max(self.end_date, d['time'])

    def print_stats(self):
        for key, stats in groupby(sorted(self.stats.iteritems()),
                                  key=lambda (k, v): (k.target, k.owner, k.duration)):
            target, owner, duration = key
            print
            print "%s's %ss by %s" % (owner, target, duration or "all time")
            curr_key, curr_val = stats.next()
            if duration:  #if there is a duration
                for d in date_iterator(self.start_date, self.end_date, duration):
                    if curr_key.time == d:
                        print curr_val,
                        try:
                            curr_key, curr_val = stats.next()
                        except StopIteration:
                            continue
                    else:
                        print 0,
                print
            else:
                print curr_val
