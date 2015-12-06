import sys
import json

def read_testbed_stats(path):
    f = open(path):
    lines = f.readlines()
    f.close()
    requests = []
    for line in xrange(1, len(lines)):
        splits = line.split()
        request = {}
        request['start_time'] = splits[1]
        request['end_time'] = splits[2]
        request['expt_idx'] = splits[3]
        request['rsrcidx'] = splits[4]
        request['action'] = splits[5]
        request['exit_code'] = splits[6]
        request['uid'] = splits[7]
        requests.append(request)

    return requests


def read_experiment_stats(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    stats = {}
    for line in xrange(1, len(lines)):
        splits = line.split()
        info = {}
        info['eid'] = splits[2]
        info['pid'] = splits[0]
        info['pid_idx'] = splits[1]
        stats[splits[6]] = info

    return stats


def read_experiment_resources(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    resources = {}
    for line in xrange(1, len(lines)):
        splits = line.split()
        resources[splits[0]] = splits[11]

    return resources


def merge(requests, stats, resources, path):
'''
    requests: list of dictionary
    stats: dictionary
    resources: dictionary
'''
    f = open(path, 'w')
    for i in xrange(0, len(requests)):
        request = requests[i]
        stat = stats[request['expt_idx']]
        request['eid'] = stat['eid']
        request['pid'] = stat['pid']
        request['pid_idx'] = stat['pid_idx']
        request['pnodes'] = resources[request['rsrcidx']]
        f.write(json.dumps(request) + '\n')
    f.close()


def main(args):
    if len(args) != 5:
        print 'Usage: <testbed_stats> <experiment_stats> <experiment_resources>'
              + '<output>'
        return 

    requests = read_testbed_stats(args[1])
    stats = read_experiment_stats(args[2])
    resources = read_experiment_resources(args[3])
    merge(requests, stats, resources, args[4])


if __name__ == '__main__':
    main(sys.args)
