import sys
import json
import datetime
import heapq
import utils
from request import Request


def simulate(requests, total_nodes):
    free_nodes = total_nodes 
    success = 0
    num_swapin = 0
    pnode_hours = 0
    swapout_experiments = set()
    swapin_experiments = {}
    failed_requests = {}
    histroy_free_nodes = [(0, free_nodes)]

    cnt = 0
    while requests:
        request = heapq.heappop(requests)
        expt_idx = request.expt_idx
        uid = request.uid
        category = request.category
        if request.action in ['swapin', 'start']:
            # only measure new users
            if category == 'new':
                num_swapin += 1
            # enough free nodes, swap in
            if free_nodes >= request.pnodes:
                if category == 'new':
                    success += 1
                # if in swapout_experiments, remove it
                if expt_idx in swapout_experiments:
                    swapout_experiments.remove(expt_idx)
                free_nodes -= request.pnodes
                swapin_experiments[expt_idx] = request
            # else the request fails
            else:
                if category == 'new':
                    failed_requests[request.idx] = request
        else:
            # maybe the previous swapin fails or this is a destroy after
            # swapout
            if expt_idx in swapout_experiments:
                continue
            if expt_idx not in swapin_experiments:
                continue
            swapout_experiments.add(expt_idx)
            req = swapin_experiments[expt_idx]
            free_nodes += req.pnodes
            pnode_hours += utils.compute_pnode_hours(
                req.pnodes, req.start_time, request.start_time)
            #check_fail_requests()
        cnt += 1
        histroy_free_nodes = [(cnt, free_nodes)]
    
    print success, num_swapin
    print 'Success rate: %lf' %(1.0 * success / num_swapin)
    print 'pnode_hours: %lf' %(pnode_hours)


def main(args):
    if len(args) != 3:
        print 'Usage: <trace> <total nodes>'
        return

    f = open(args[1], 'r')
    requests = []
    for line in f:
        request = json.loads(line)
        heapq.heappush(requests, Request(request))
    f.close()

    simulate(requests, int(args[2]))


if __name__ == '__main__':
    main(sys.argv)
