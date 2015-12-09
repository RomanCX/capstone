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


def simulate(requests, total_nodes):
    free_nodes = total_nodes 
    success = 0
    num_swapin = 0
    pnode_hours = 0
    swapout_experiments = set()
    swapin_experiments = {}
    failed_requests = {}
    histroy_free_nodes = [(0, free_nodes)]

    for i in xrange(0, len(requests)):
        request = requests[i]
        expt_idx = request['expt_idx']
        uid = request['uid']
        category = request['category']
        if request['action'] in ['swapin', 'start']:
            # only measure new users
            if category == 'new_user':
                num_swapin += 1
            # enough free nodes, swap in
            if free_nodes >= request['pnodes']:
                # if in swapout_experiments, remove it
                if expt_idx in swapout_experiments:
                    swapout_experiments.remove(expt_idx)
                free_nodes -= request['pnodes']
                success += 1
                swapin_experiments[expt_idx] = request
            # else the request fails
            else:
                failed_requests[request['idx']] = request
        else:
            # maybe the previous swapin fails or this is a destroy after
            # swapout
            if expt_idx in swapout_experiments:
                continue
            if expt_idx not in swapin_experiments:
                continue
            swapout_experiments.add(expt_idx)
            exp = swapin_experiments[expt_idx]
            free_nodes += exp['pnodes']
            pnode_hours += compute_pnode_hours(
                int(exp['pnodes'], exp['end_time'], request['start_time'])
            #check_fail_requests()
        
        histroy_free_nodes = [(i + 1, free_nodes)]

    print 'Success rate: %lf' %(1.0 * success / num_swapin)
    print 'pnode_hours: %lf' %(pnode_hours)


def main(args):
    if len(args) != 3:
        print 'Usage: <trace> <total nodes>'
        return

    requests = []
    for line in f:
        request = json.loads(line)
        requests.append(request)
    f.close()
    
    simulate(requests, int(args[2]))


if __name__ == '__main__':
    main(sys.argv)
