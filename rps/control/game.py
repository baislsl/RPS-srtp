from ..models import Record
import threading
import time
from django.utils import timezone
import random

R = 0
P = 1
S = 2

# 是否生成虚拟玩家
use_virtual_player = False


class VirtualPlayer:
    def __init__(self, id, game):
        self.id = id
        self.game = game

    def loop(self):
        # TODO: remove such naive code
        while True:
            self.game.insert(self.id, self.next_action())
            self.game.wait_competitor_result()
            time.sleep(4)

    def start(self):
        threading.Thread(target=self.loop, name="loop" + self.id).start()

    def next_action(self):
        """
        在这里接入模型，需要数据可以调用game的借口
        :return:
        """
        return random.randint(0, 2)


class GameManager:
    game_pool = []
    game_pool_lock = threading.Lock()

    waiting_semaphore = threading.Semaphore(2)
    waiting_pool = []
    waiting_game = None
    waiting_condition = threading.Condition()

    def __init__(self):
        pass

    def of(self, id):
        result = None
        self.game_pool_lock.acquire()
        for game in self.game_pool:
            if game.id1 == id or game.id2 == id:
                result = game
        self.game_pool_lock.release()
        if result is None:
            result = self.create_game(id)
            self.game_pool.append(result)
        return result

    def create_game(self, id, try_use_virtual_player=True):
        """
        暂时随机生成对手
        TODO: 实际中如果人人队长需要阻塞等待另一名对手的产生
        :param id:
        :return:
        """
        self.waiting_semaphore.acquire()
        self.waiting_pool.append(id)
        self.waiting_condition.acquire()
        threading.Thread(target=self.notify_pool_handler, name="loop" + id).start()
        print(id, ": waiting...")

        if try_use_virtual_player and use_virtual_player:
            threading.Thread(target=self.generate_virtual_player, name="virtual player generate",
                             args=('vir-' + id,)).start()

        self.waiting_condition.wait()
        self.waiting_condition.release()
        self.waiting_semaphore.release()
        print(id, ": get result")
        return self.waiting_game

    def notify_pool_handler(self):
        """
        检查是否有两个玩家在pool中，如果有，就为这两位玩家生成一个游戏平台
        """
        print("waiting pool:", self.waiting_pool)
        if len(self.waiting_pool) == 2:
            self.waiting_condition.acquire()
            self.waiting_game = Game(self.waiting_pool[0], self.waiting_pool[1])
            self.waiting_pool = []
            self.waiting_condition.notify_all()
            self.waiting_condition.release()

    def generate_virtual_player(self, id):
        print("generating virtual player ", id)
        game = self.create_game(id, False)
        player = VirtualPlayer(id, game)
        player.start()
        return game


class Game:
    id1_last_action = -1
    id2_last_action = -1
    finished = True
    lock = threading.Lock()
    last_record = None
    count = 0

    def __init__(self, id1, id2):
        self.id1 = id1
        self.id2 = id2
        self.competition_id = id1 + "_" + id2

    def history(self, count=-1):
        """
        query history data order by date
        :param count:
        :return:
        """
        record_list = Record.objects.filter(competition_id=self.competition_id).order_by('-date')
        if count == -1:
            return record_list
        else:
            return record_list[0: count]

    def insert(self, id, action):
        """
        insert next action
        :param id: from id
        :param action: action of player
        """
        self.lock.acquire()
        if id == self.id1:
            self.id1_last_action = action
        elif id == self.id2:
            self.id2_last_action = action
        else:
            raise RuntimeWarning("incorrect id input, id show between %s and %s, but input id is %s" %
                                 self.id1, self.id2, id)

        if self.id1_last_action != -1 and self.id2_last_action != -1:
            # insert new record to database
            record = self.generate_record()
            record.save()
            self.last_record = record
            self.finished = True
            self.id1_last_action = self.id2_last_action = -1
        else:
            self.finished = False
        self.lock.release()

    def try_last_result(self):
        """
        不阻塞的获取等待情况
        :return: 如果自己和对方都已经在该轮中给出决策或都没给出，返回True
                    如果只有一方给出，返回False
        """
        self.lock.acquire()
        result = self.finished
        self.lock.release()
        return result

    def wait_competitor_result(self):
        """
        阻塞等待对手的结果
        :return:
        """
        # TODO: remove such naive code
        while True:
            self.lock.acquire()
            result = self.finished
            record = self.last_record
            self.lock.release()
            if result:
                return record
            time.sleep(1)

    def generate_record(self):
        record = Record()
        record.id1 = self.id1
        record.id2 = self.id2
        record.competition_id = self.competition_id
        record.action1 = self.id1_last_action
        record.action2 = self.id2_last_action
        record.date = timezone.now()
        record.count = self.count
        self.count = self.count + 1
        return record
