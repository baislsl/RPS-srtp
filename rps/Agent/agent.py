import numpy as np
import mxnet as mx
from mxnet import nd, init, gluon, autograd
from . import net



# action: r:0, p:1, s:2
class Agent:
    def __init__(self, his_len=2, epoch_len=2, lr=0.5):
        self.first = 0
        # TODO: add RNN to handle history if possible
        self.his_len = his_len  # length of history to look at(also the length of )
        self.his = np.zeros((2, self.his_len)) # 2D array recording our actions and opponent actions
        self.epoch_len = epoch_len
        self.default_epoch_len = epoch_len
        self.reward = np.zeros((self.epoch_len * 2))
        self.last_action = None
        # self.confidence = np.zeros((1))  # confidence defined as weighted sum of
        # winning rate(0.7) and not-losing rate(0.3)
        self.threshold_low = 0.33
        self.threshold_high = 0.7
        #self.val_map = {"r": 0, "p": 1, "s": 2, "l": 0, "t": 1, "w": 2, "-": 0, "o": 1, "+": 2}
        #self.action_map = ['r', 'p', 's']
        # self.opponent_friendliness = np.zeros((1))
        # opponent friendliness defined as std of opponent policy
        self.net = net.AgentNet()
        self.net.initialize(init=init.Xavier())
        self.lr = lr
        self.default_lr = lr
        self.trainer = gluon.Trainer(self.net.collect_params(),
                                     'sgd', {'learning_rate': self.lr})

    # return a action given current information
    def action(self):
        # first action, when there is no enough data
        if self.first < self.his_len:
            # take turn to return 0, 1, 0, 1, ...
            if self.get_confidence() > self.threshold_high:
                our_action = self.first % 2
            else:
                our_action = np.random.randint(2)#self.first % 2
            self.first += 1
        else: # his is ready to feed
            # if we are losing, we change our strategy more rapidly
            # by (changing lr in gradient descent) or smaller epoch size?
            confidence = self.get_confidence()
            if confidence < self.threshold_low:
                #self.lr = 3 * self.default_lr
                #self.trainer.set_learning_rate(self.lr)
                self.epoch_len = max(round(self.default_epoch_len / 3), 1)
            elif confidence > self.threshold_high:
                self.lr = 1/3 * self.default_lr
                self.trainer.set_learning_rate(self.lr)
                self.epoch_len = round(self.default_epoch_len * 1.5)
            else:
                if self.lr != self.default_lr:
                    self.lr = self.default_lr
                    self.trainer.set_learning_rate(self.lr)
                if self.epoch_len != self.default_epoch_len:
                    self.epoch_len = self.default_epoch_len

            # collect info for EPOCH_SIZE epochs and then change the policy
            info = nd.zeros((1, 2))
            info[0, 0] = self.get_confidence()
            info[0, 1] = self.get_opponent_friendliness()
            input_arr = self.his2num()
            rewards = nd.array(self.reward[:self.epoch_len].reshape(1, -1))
            pro = self.get_policy(input_arr, info, rewards)
            our_action = self.generate_action(pro)

        # append out_action to self.his[0]
        self.last_action = our_action
        return our_action


    # after each round is over, we can get some feedback
    # update bookkeeping info: his and reward
    # also we update our confidence and opponent friendliness
    def feedback_update(self, actions, rewards):
        self.his = actions
        self.reward = rewards

    # we put our history and info(our confidence and opponent friendliness)
    # and get a policy using neural network
    def get_policy(self, input_arr, info, rewards, file_name='checkpt/net.params', pretrain=False):
        if pretrain:
            self.net.load_params(file_name)
        with autograd.record():
            out_policy = self.net(input_arr, info)
        head_grad = net.policy_gradient(out_policy, rewards)
        out_policy.backward(head_grad)
        self.trainer.step(1) # backpropagation
        self.net.save_params(file_name)
        return out_policy


    def get_confidence(self, alpha=0.7):
        # return alpha * win_rate + (1-alpha)*not_lose_rate
        win_time = tie_time = 0
        for i in range(self.his_len):
            if self.his[0, i] == self.his[1, i]:
                tie_time += 1
            elif (self.his[0, i] + 2 - self.his[1, i]) % 3 == 0:
                win_time += 1
        return (alpha * win_time + (1-alpha) * tie_time)/self.his_len


    def get_opponent_friendliness(self):
        opponent_his = self.his[1]
        return np.std(opponent_his)

    def generate_action(self, p): # p shape(1,3), probability of choosing each action
        rand = np.random.rand()
        if rand <= p[0]:
            return 0
        elif rand <= p[0] + p[1]:
            return 1
        else:
            return 2


    def his2num(self):
        # turn a 3D array history to 1D array of number as the input of neural net
        # one entry of history: action(3), action(3)
        return self.his[0] * 3 + self.his[1]





