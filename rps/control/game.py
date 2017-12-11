from ..models import Record
import threading
import time
from django.utils import timezone


class GameManager:
    def __init__(self, id):
        pass


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
        record_list = Record.objects.filter(compare_id=self.competition_id).order_by('-date')
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
        self.lock.require()
        result = self.finished
        self.lock.release()
        return result

    def wait_last_result(self):
        """
        阻塞等待对手的结果
        :return:
        """
        # TODO: remove such naive code
        while True:
            self.lock.require()
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
