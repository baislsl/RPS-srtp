def int2rps(i):
    if i == 0:
        return 'R'
    elif i == 1:
        return 'P'
    else:
        return 'S'


def int2word(i):
    if i == 0:
        return '石头'
    elif i == 1:
        return '布'
    else:
        return '剪刀'


def earn(action1, action2):
    table = [
        [0, -1, 1],
        [1, 0, -1],
        [-1, 1, 0]
    ]
    return table[action1][action2]
