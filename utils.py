import datetime


date_format = '%Y-%m-%d %H:%M:%S'


def parse_time(s):
    return datetime.datetime.strptime(s, date_format)


def format_time(t):
    return t.strftime(date_format)


def compute_pnode_hours(pnodes, start_time, end_time):
    start = parse_time(start_time)
    end = parse_time(end_time)
    duration = end - start
    hours = duration.total_seconds() / 3600.0
    return pnodes * hours
