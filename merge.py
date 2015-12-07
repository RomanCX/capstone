import sys
import json

def read_testbed_stats(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    requests = []
    for i in xrange(1, len(lines)):
        splits = lines[i].split('\t')
        # exit not 0
        if int(splits[6]) != 0:
            continue
        # action is not swap in or swap out
        if splits[5] not in ['swapin', 'swapout']:
            continue
        request = {}
        request['idx'] = splits[0]
        request['start_time'] = splits[1]
        request['end_time'] = splits[2]
        request['expt_idx'] = splits[3]
        request['rsrcidx'] = splits[4]
        request['action'] = splits[5]
        request['uid'] = splits[7]
        requests.append(request)

    return requests


def read_experiment_stats(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    stats = {}
    for i in xrange(1, len(lines)):
        splits = lines[i].split('\t')
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
    for i in xrange(1, len(lines)):
        splits = lines[i].split('\t')
        resources[splits[0]] = splits[11]

    return resources


def print_tsv(request, f):
    f.write(request['idx'] + '\t' + request['pid'] + '\t' + request['pid_idx']
            + '\t' + request['eid'] + '\t' + request['expt_idx'] + '\t'
            + request['uid'] + '\t' + request['action'] + '\t'
            + request['start_time'] + '\t' + request['end_time'] + '\t'
            + request['pnodes'] + '\n')


def merge(requests, stats, resources, path):
    '''requests: list of dictionary
       stats: dictionary
       resources: dictionary
    '''
    fjson = open(path + '_json', 'w')
    ftsv = open(path + '_tsv', 'w')
    for i in xrange(0, len(requests)):
        request = requests[i]
        if request['expt_idx'] not in stats:
            continue
        if request['rsrcidx'] not in resources:
            continue
        stat = stats[request['expt_idx']]
        request['eid'] = stat['eid']
        request['pid'] = stat['pid']
        request['pid_idx'] = stat['pid_idx']
        request['pnodes'] = resources[request['rsrcidx']]
        fjson.write(json.dumps(request) + '\n')
        print_tsv(request, ftsv)

    fjson.close()
    ftsv.close()

def main(args):
    if len(args) != 5:
        print ('Usage: <testbed_stats> <experiment_stats> <experiment_resources>'
               + ' <output>')
        return 

    requests = read_testbed_stats(args[1])
    stats = read_experiment_stats(args[2])
    resources = read_experiment_resources(args[3])
    merge(requests, stats, resources, args[4])


if __name__ == '__main__':
    main(sys.argv)
