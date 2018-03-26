from ..models import Record
from django.utils import timezone
from ..Agent import agent
import numpy as np
from ..util import util
from . import history

user_count = 1
robot_name = 'robot_rps'


class Platform:
    response_count = 0
    response_infos = {}
    counter = 0  # 轮数
    dic = {}  # 对手匹配情况
    in_robot = False  # 是否使用AI

    def __init__(self):
        self.agent = agent.Agent()

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
        if self.agent.first >= leng:
            our_record1 = list(Record.objects.filter(id1=robot_name).order_by('count'))[-leng:]
            our_record2 = list(Record.objects.filter(id2=robot_name).order_by('count'))[-leng:]
            our_actions = [(record.action1,record.count) for record in our_record1]
            our_actions.extend([(record.action2, record.count) for record in our_record2])
            sorted(our_actions, key=lambda x:x[1], reverse=True)
            our_actions = [our_actions[i][0] for i in range(self.agent.his_len)]
            oppo_record1 = list(Record.objects.filter(id1=id).order_by('count'))[-leng:]
            oppo_record2 = list(Record.objects.filter(id2=id).order_by('count'))[-leng:]
            oppo_actions = [(record.action1, record.count) for record in oppo_record1]
            oppo_actions.extend([(record.action2, record.count) for record in oppo_record2])
            sorted(oppo_actions, key=lambda x: x[1], reverse=True)
            oppo_actions = [oppo_actions[i][0] for i in range(self.agent.his_len)]
            print('our', our_actions)
            print('oppo',oppo_actions)
            rewards = np.zeros((1, self.agent.epoch_len))
            for i in range(1, self.agent.epoch_len + 1):
                print('our:', our_actions[-i])
                rewards[:, -i] = util.earn(int(our_actions[-i]), int(oppo_actions[-i]))

            # actions (2, his_len), rewards (1, epoch_len)
            actions = np.concatenate(([our_actions[-self.agent.epoch_len:]], [oppo_actions[-self.agent.epoch_len:]]),
                                     axis=0)
            self.agent.feedback_update(actions, rewards)

        our_action = self.agent.action()

        print("response for ", id, "action ", our_action)

        return our_action

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
