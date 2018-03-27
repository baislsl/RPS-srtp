from rps.util import util
from django.test import TestCase
import numpy as np
import mxnet as mx
from mxnet import nd, init, gluon, autograd
from rps.Agent import net
from .models import Record
from rps.Agent.agent import Agent


class TestClass(TestCase):

    def test_agent(self):
        records = []
        robot_name = 'robot'
        agent = Agent()
        leng = max(agent.epoch_len, agent.his_len)
        for i in range(agent.epoch_len):
            record = Record()
            record.action2 = agent.action('12')
            record.id2 = robot_name
            record.action1 = 0
            record.id1 = '12'

            records.append(record)

        for i in range(20):
            our_actions = [r.action(robot_name) for r in records][-leng:]
            oppo_actions = [r.action('12') for r in records][-leng:]

            print('our', our_actions)
            print('oppo', oppo_actions)

            rewards = np.zeros((1, agent.epoch_len))
            for i in range(1, agent.epoch_len + 1):
                print('i=', i)
                print('our:', our_actions[-i])
                rewards[:, -i] = util.earn(int(our_actions[-i]), int(oppo_actions[-i]))

            # actions (2, his_len), rewards (1, epoch_len)
            actions = np.concatenate(([our_actions[-agent.epoch_len:]], [oppo_actions[-agent.epoch_len:]]),
                                     axis=0)
            agent.feedback_update(actions, rewards)

            record = Record()
            record.action2 = agent.action('12')
            record.action1 = i % 2
            record.id1 = '12'
            record.id2 = robot_name
            records.append(records)

