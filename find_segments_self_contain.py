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
    return difference.days >= 31


def find_segments(requests):
    swapin_experiments = {}
    swapout_experiments = set()
    users = set()
    pnode_hours = 0
    start = 0
    cur = 0
    segment_id = 0
    segment_stats = []
    segment_data = []
    segments = []

    total = len(requests)
    while cur < total: 
        request = requests[cur]
        # we meet a boundary
        if is_new_segment(request['start_time'], requests[start]['start_time']):
            # there's still experiments that are not swapped out
            if len(swapin_experiments) > 0:
                # keep scanning until all experiments are swapped out
                # ignore all experiments that are swapped in during this process
                while cur < total:
                    request = requests[cur]
                    if (request['action'] in ['swapout', 'destroy'] and
                        request['expt_idx'] in swapin_experiments):
                        tmp = swapin_experiments[request['expt_idx']]
                        pnode_hours += compute_pnode_hours(
                            int(tmp['pnodes']), tmp['time'], request['start_time'])
                        segment_data.append(request)
                        del swapin_experiments[request['expt_idx']]
                        if len(swapin_experiments) == 0:
                            cur += 1
                            break
                    cur += 1

            segment_stats.append(
                (pnode_hours, len(users), 
                 requests[start]['idx'], requests[cur - 1]['idx'],
                 requests[start]['start_time'], requests[cur - 1]['start_time'],
                 segment_id))
            segments.append(segment_data)
            pnode_hours = 0
            users = set()
            start = cur
            segment_data = []
            segment_id += 1

        segment_data.append(requests)
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
                cur += 1
                continue
            if expt_idx not in swapin_experiments:
                cur += 1
                continue
            swapout_experiments.add(expt_idx)
            tmp = swapin_experiments[expt_idx]
            pnode_hours += compute_pnode_hours(
                int(tmp['pnodes']), tmp['time'], request['start_time'])
            del swapin_experiments[expt_idx]

        cur += 1

    return segment_stats, segments


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

    segment_stats, segments = find_segments(requests)            
    segment_stats = sorted(segment_stats, key=lambda x : x[0] / x[1], reverse=True)
    for segment_stat in segment_stats:
        print segment_stat[0] / segment_stat[1], segment_stat
   

if __name__ == '__main__':
    main(sys.argv)
