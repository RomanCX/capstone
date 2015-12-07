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


def get_user_usage(requests):
    swapin_experiments = {}
    swapout_experiments = set()
    user_usage = {}

    for request in requests:
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
        else:
            # destroy after swapout
            if expt_idx in swapout_experiments:
                continue
            if expt_idx not in swapin_experiments:
                continue
            swapout_experiments.add(expt_idx)
            tmp = swapin_experiments[expt_idx]
            pnode_hours = compute_pnode_hours(
                int(tmp['pnodes']), tmp['time'], request['start_time'])

            if uid not in user_usage:
                user_usage[uid] = pnode_hours
            else:
                user_usage[uid] += pnode_hours
    
    return user_usage


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

    user_usage = get_user_usage(requests)            
    items = user_usage.items()
    items = sorted(items, key=lambda item:item[1], reverse=True)
    for item in items:
        print item


if __name__ == '__main__':
    main(sys.argv)
