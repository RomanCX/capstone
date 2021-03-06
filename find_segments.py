import sys
import json
import datetime
import copy


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
                cnt = 1
                for expt_idx in swapin_experiments.keys():
                    old_request = swapin_experiments[expt_idx]
                    request = copy.deepcopy(old_request)
                    request['idx'] = str(int(requests[cur - 1]['idx']) + cnt)
                    request['action'] = 'swapout'
                    request['start_time'] = requests[cur - 1]['end_time']
                    pnode_hours += compute_pnode_hours(
                        int(old_request['pnodes']), old_request['start_time'],
                        request['start_time'])
                    cnt += 1
                    segment_data.append(request)

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

        expt_idx = request['expt_idx']
        uid = request['uid']
        if request['action'] in ['swapin', 'start']:
            segment_data.append(request)
            if expt_idx in swapout_experiments:
                swapout_experiments.remove(expt_idx)
            swapin_experiments[expt_idx] = request
            users.add(request['uid'])
        else:
            # destroy after swapout
            if expt_idx in swapout_experiments:
                cur += 1
                continue
            if expt_idx not in swapin_experiments:
                cur += 1
                continue
            segment_data.append(request)
            swapout_experiments.add(expt_idx)
            tmp = swapin_experiments[expt_idx]
            pnode_hours += compute_pnode_hours(
                int(tmp['pnodes']), tmp['start_time'], request['start_time'])
            del swapin_experiments[expt_idx]

        cur += 1

    return segment_stats, segments


def main(args):
    if len(args) != 3:
        print 'Usage: <trace> <output>'
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
   
    for i in xrange(len(segments)):
        f = open(args[2] + '/segment_' + str(i), 'w')
        segment_data = segments[i]
        print 'outputing %dth segment' %(i)
        for request in segment_data:
            f.write(json.dumps(request))
            f.write('\n')
        f.close()


if __name__ == '__main__':
    main(sys.argv)
