from ..models import Record
from django.utils import timezone

user_count = 2
robot_name = 'robot_rps'


class Platform:
    response_count = 0
    response_infos = {}
    counter = 0  # 轮数
    dic = {}  # 对手匹配情况
    in_robot = False

    def __init__(self):
        pass

    def set_user_response(self, id, action):
        self.response_count += 1
        self.response_infos[id] = action

    def is_full(self):
        return self.response_count == user_count

    def is_empty(self):
        return self.response_count == 0

    def fetch_robot_response(self, id):
        # TODO: insert AI interface
        return 0

    def dump_log(self):
        if not self.is_full():
            return

        if len(self.dic.keys()) == 0:
            self.match_dict()

        self.counter += 1

        for id1 in self.dic.keys():
            id2 = self.dic[id1]
            if id2 == robot_name:  # human vs robot
                record = Record()
                record.id1 = id1
                record.id2 = robot_name
                record.competition_id = id1 + ":" + robot_name
                record.action1 = self.response_infos[id1]
                # get robot response
                record.action2 = self.fetch_robot_response(id1)

                record.date = timezone.now()
                record.count = self.counter
                record.save()
            else:  # human vs human
                record = Record()
                record.id1 = id1
                record.id2 = id2
                record.competition_id = id1 + ":" + id2
                record.action1 = self.response_infos[id1]
                record.action2 = self.response_infos[id2]
                record.date = timezone.now()
                record.count = self.counter
                record.save()

        self.response_infos = {}
        self.response_count = 0

    '''
    匹配对手
    '''

    def match_dict(self):
        ids = []
        for i in self.response_infos.keys():
            ids.append(i)

        key = None
        for id in ids:
            if key is None:
                key = id
            else:
                self.dic[key] = id
                key = None
        return

    def switch_robot(self):
        self.in_robot = True
        ids = []
        for id1 in self.dic.keys():
            id2 = self.dic[id1]
            ids.append(id1)
            ids.append(id2)

        for id in ids:
            self.dic[id] = robot_name
