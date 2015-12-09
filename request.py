import utils


class Request:
    
    def __init__(self, request):
        self.idx = request['idx']
        self.expt_idx = request['expt_idx']
        self.pnodes = int(request['pnodes'])
        self.uid = request['uid']
        self.pid_idx = request['pid_idx']
        self.action = request['action']
        if 'new_time' in request:
            self.start_time = request['new_time']
            self.category = 'new'
        else:
            self.start_time = request['start_time']
            self.category = 'old'

    def __cmp__(self, obj):
        time_a = utils.parse_time(self.start_time)
        time_b = utils.parse_time(obj.start_time)
        idx_a = int(self.idx)
        idx_b = int(obj.idx)
        if time_a == time_b:
            if idx_a < idx_b:
                return -1
            if idx_a == idx_b:
                return 0
            if idx_a > idx_b:
                return 1
        if time_a < time_b:
            return -1
        return 1

    def __str__(self):
        return self.idx + ' ' + self.start_time  + ' ' + self.category
