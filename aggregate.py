"""Module for parsing a log file and aggregating analytics
"""
import argparse
from datetime import datetime
import funcutils
from field import Field
from aggregator import Aggregator
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


if __name__ == "__main__":
    args = parse_args()
    aggregator = Aggregator(args.field)
    line_parser = funcutils.and_then(json.loads, convert_timestamp)
    for r in iterate_records(args.filename, line_parser):
        aggregator.add(r)
    aggregator.print_stats()
