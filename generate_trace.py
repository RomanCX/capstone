import sys
import json
import datetime
import utils


def main(args):
    if len(args) != 5:
        print 'Usage: <trace> <segment> <user_ids> <output>'
        return

    f = open(args[1], 'r')
    requests = []
    for line in f:
        request = json.loads(line)
        requests.append(request)
    f.close()

    f = open(args[2], 'r')
    segments = []
    for line in f:
        request = json.loads(line)
        segments.append(request)
    f.close()

    user_requests = {}
    f = open(args[3], 'r')
    for line in f:
        line = line[:-1]
        user_requests[line] = []
    f.close()

    start_date = segments[0]['start_time'].split()[0]
    is_full = set()

    cnt = 0

    for request in requests:
        uid = request['uid']

        if uid in user_requests and uid not in is_full:
            cnt += 1
            # each request has an unique id
            request['idx'] = str(int(segments[-1]['idx']) + cnt)
            # avoid using same expt_idx in segment
            request['expt_idx'] = 'zfeng' + request['expt_idx']
            request['uid'] = 'zfeng' + uid
            req_list = user_requests[uid]
            if len(req_list) == 0:
                splits = request['start_time'].split()
                # new_time = replace date
                request['new_time'] = start_date + ' ' + splits[1]
            else:
                start_time = utils.parse_time(req_list[0]['start_time'])
                cur_time = utils.parse_time(request['start_time'])
                diff = cur_time - start_time
                if diff.days >= 31:
                    is_full.add(uid)
                    continue
                start_new_time = utils.parse_time(req_list[0]['new_time'])
                cur_new_time = start_new_time + diff
                # new_time = new_time of first request + difference
                request['new_time'] = utils.format_time(cur_new_time)

            req_list.append(request)

    f = open(args[4], 'w')
    # output requests in segment
    for request in segments:
        f.write(json.dumps(request) + '\n')
    # output requests in users
    for uid in user_requests.keys():
        req_list = user_requests[uid]
        print uid, len(req_list)
        for request in req_list:
            f.write(json.dumps(request) + '\n')
    f.close()
    

if __name__ == '__main__':
    main(sys.argv)
