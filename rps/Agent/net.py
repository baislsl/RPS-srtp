import numpy as np
import mxnet as mx
from mxnet import nd, autograd, gluon


class ConcatNet(gluon.nn.Block):
    def __init__(self,net1,**kwargs):
        super(ConcatNet,self).__init__(**kwargs)
        self.net1 = net1
    def forward(self,x1,x2):
        return nd.concat(*(x1, self.net1(x2)))


class AgentNet(gluon.nn.Block):
    def __init__(self, units1=200, units2=1024, **kwargs):
        super(AgentNet, self).__init__(**kwargs)
        self.units1 = units1
        self.units2 = units2
        self.net = ConcatNet(gluon.nn.Dense(self.units1, activation='relu'))
        self.net2 = gluon.nn.Dense(self.units2, activation='relu')
        self.net3 = gluon.nn.Dense(3)

# given a policy, return a gradient
# policy: shape(1, 3), probability of choosing each action
# rewards: reward using this policy, shape (1, epoch_len)
def policy_gradient(policy, rewards, lr=1, gamma=0.9, small=1e-8,
                    clip=False, theta=1e8): # small helps it to be stable
    T = rewards.shape[1]
    # head_grad = nd.zeros_like(policy)
    factor = 0
    for t in range(T):
        G = rewards[:, t:T].sum()
        factor += gamma**t * G
    grad = -lr * factor * (1/(policy+small))      # to match gradient descent
    if clip:
        if np.any((grad.asnumpy() > theta)):
           grad[:] *= theta / nd.sum(grad**2)
    return grad


