import sys
import json
import datetime


datetime_format = '%Y-%m-%d %H:%M:%S'


def compute_pnode_hours(pnodes, start_time, end_time):
    start = datetime.datetime.strptime(start_time, datetime_format)
    end = datetime.datetime.strptime(end_time, datetime_format)
    duration = end - start
    hours = duration.total_seconds() / 3600.0
    return pnodes * hours


def is_new_segment(current_time, start_time):
    current_time = datetime.datetime.strptime(current_time, datetime_format)
    start_time = datetime.datetime.strptime(start_time, datetime_format)
    difference = current_time - start_time
    return difference.days >= 14


def find_segments(requests):
    swapin_experiments = {}
    swapout_experiments = set()
    users = set()
    pnode_hours = 0
    start = 0
    segments = []

    for i in xrange(0, len(requests)):
        request = requests[i]
        if is_new_segment(request['start_time'], requests[start]['start_time']):
            segments.append((pnode_hours, len(users), 
                             requests[start]['idx'], requests[i - 1]['idx']))
            pnode_hours = 0
            users = set()
            start = i
        expt_idx = request['expt_idx']
        uid = request['uid']
        if request['action'] in ['swapin', 'start']:
            if expt_idx in swapout_experiments:
                swapout_experiments.remove(expt_idx)
            tmp = {}
            tmp['uid'] = request['uid']
            tmp['pnodes'] = request['pnodes']
            tmp['time'] = request['end_time']
            swapin_experiments[expt_idx] = tmp
            users.add(request['uid'])
        else:
            # destroy after swapout
            if expt_idx in swapout_experiments:
                continue
            if expt_idx not in swapin_experiments:
                continue
            swapout_experiments.add(expt_idx)
            tmp = swapin_experiments[expt_idx]
            pnode_hours += compute_pnode_hours(
                int(tmp['pnodes']), tmp['time'], request['start_time'])
                 
    return segments


def main(args):
    if len(args) != 2:
        print 'Usage: <trace>'
        return

    f = open(args[1], 'r')
    requests = []
    for line in f:
        request = json.loads(line)
        requests.append(request)
    f.close()

    segments = find_segments(requests)            
    segments = sorted(segments, key=lambda x : (x[0], x[1]), reverse=True)
    for segment in segments:
        print segment


if __name__ == '__main__':
    main(sys.argv)
