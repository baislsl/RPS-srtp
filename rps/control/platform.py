from ..models import Record
from django.utils import timezone
from ..Agent import agent
import numpy as np
from ..util import util
from django.db.models import Q

user_count = 2
robot_name = 'robot_rps'


class Platform:
    response_count = 0
    response_infos = {}
    counter = 0  # 轮数
    dic = {}  # 对手匹配情况
    in_robot = False  # 是否使用AI

    def __init__(self):
        self.agent = agent.Agent(his_len=5, epoch_len=5
                                 , debug=True, lr=0.6)

    '''
    输入实验者当前轮的决策
    '''

    def set_user_response(self, id, action):
        self.response_count += 1
        self.response_infos[id] = action

    def is_full(self):
        return self.response_count == user_count

    def is_empty(self):
        return self.response_count == 0

    def fetch_robot_response(self, id, action):
        # TODO: insert AI interface
        # 需要的数据在数据库中可以查找,参考history.py

        leng = max(self.agent.epoch_len, self.agent.his_len)
        if self.agent.id_first(id) >= leng:
            query_set = Record.objects \
                .filter(Q(id1=robot_name) | Q(id2=robot_name)) \
                .filter(Q(id1=id) | Q(id2=id)) \
                .order_by('count')
            our_actions = [r.action(robot_name) for r in query_set][-leng:]
            oppo_actions = [r.action(id) for r in query_set][-leng:]

            print('our', our_actions)
            print('oppo', oppo_actions)

            rewards = np.zeros((1, self.agent.epoch_len))
            for i in range(1, self.agent.epoch_len + 1):
                #print('i=', i)
                #print('our:', our_actions[-i])
                rewards[:, -i] = util.earn(int(our_actions[-i]), int(oppo_actions[-i]))

            # actions (2, his_len), rewards (1, epoch_len)
            actions = np.concatenate(([our_actions[-self.agent.his_len:]], [oppo_actions[-self.agent.his_len:]]),
                                     axis=0)
            self.agent.feedback_update(actions, rewards)

        our_actions = self.agent.action(id)

        print("response for ", id, "action ", our_actions)

        return our_actions

    '''
    将一轮里所有数据写入数据库
    '''

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
                record.action2 = self.fetch_robot_response(id1, record.action1)

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

    '''
    切换到 human vs AI
    '''

    def switch_robot(self):

        if self.in_robot:  # 已经切换过了
            return

        self.in_robot = True
        ids = []
        for id1 in self.dic.keys():
            id2 = self.dic[id1]
            ids.append(id1)
            ids.append(id2)

        for id in ids:
            self.dic[id] = robot_name
