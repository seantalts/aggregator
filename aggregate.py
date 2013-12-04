"""Module for parsing a log file and aggregating analytics
"""
import argparse
from datetime import datetime
import utils
from field import Field, date_iterator
from collections import defaultdict
from itertools import groupby
try:
    import simplejson as json
except ImportError:
    import json


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process event dump and generate analytics.")
    parser.add_argument("--filename", help="filename to parse", required=True)
    parser.add_argument("--field",
                        help="fields we want to aggregate over, if present."
                        "  Examples: 'follow/day/vendor' or 'follow/vendor' "
                        "for total over all time present in the log file",
                        action="append",
                        default=[])
    args = parser.parse_args()
    if not args.field:
        args.field = ["follow/day/vendor",
                      "favorite/day/vendor",
                      "favorite/day/product",
                      "total/day/vendor",
                      "follow/vendor",
                      "total/product"
                      ]
    args.field = [Field(f) for f in args.field]
    return args


def convert_timestamp(dict_):
    if "time" in dict_:
        dict_["time"] = datetime.fromtimestamp(dict_["time"])
    return dict_


def iterate_records(filename, line_parser=json.loads):
    for line in open(filename):
        yield line_parser(line)


class Aggregator(object):
    def __init__(self, targets):
        self.targets = targets
        self.stats = defaultdict(int)
        self.start_date = datetime(9999, 1, 1)
        self.end_date = datetime(1, 1, 1)

    def __str__(self):
        return "Aggregator(%s)" % (", ".join(map(str, self.targets)),)

    def add(self, d):
        for target in self.targets:
            val = target.value(d)
            if val:
                self.stats[target.key(d)] += val  #XXX use generic aggregator functions
                self.start_date = min(self.start_date, d['time'])
                self.end_date = max(self.end_date, d['time'])

    def print_stats(self):
        for key, stats in groupby(sorted(self.stats.iteritems()),
                                  key=lambda (k, v): (k.target, k.owner, k.duration)):
            target, owner, duration = key
            print
            print "%s's %ss by %s" % (
                owner,
                target,
                duration or "all time")
            curr_key, curr_val = stats.next()
            if duration:  #if there is a duration
                for d in date_iterator(self.start_date, self.end_date, duration):
                    if curr_key.time == d:
                        print curr_val,
                        curr_key, curr_val = stats.next()
                    else:
                        print 0,
                print
            else:
                print curr_val




if __name__ == "__main__":
    args = parse_args()
    aggregator = Aggregator(args.field)
    line_parser = utils.and_then(json.loads, convert_timestamp)
    for r in iterate_records(args.filename, line_parser):
        aggregator.add(r)
    aggregator.print_stats()
