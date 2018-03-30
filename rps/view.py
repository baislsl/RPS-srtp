from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models import Record
from django.utils import timezone
from django.http import JsonResponse
import json
import time
from .util import util
from .control.platform import Platform
from .control.history import History
from django.db.models import Q

# game_manager = GameManager()
platform = Platform()


# 配置页面，选择从human vs human切换到human vs AI
def configure(request):
    if request.method == 'POST':
        id = request.POST['id']
        if id == 'baislsl':
            platform.switch_robot()
            print("platform switch to robot now")
    return render(request, 'rps/configure.html', {})


def index(request):
    context = {}
    return render(request, 'rps/index.html', context)


def play(request):
    id = request.POST['id']
    print("id: ", id)

    # create a game for this player
    context = {"id": id}

    return render(request, 'rps/play.html', context)


def handon(request, debug=False):
    id = request.POST['id']
    data = {"info": "handon return"}
    if debug:
        print(request.POST)

    if request.method == 'POST':
        if request.is_ajax():
            action = -1
            if debug:
                print(type(request.POST['action_r']))
            if request.POST['action_r'] == 'true':
                action = 0
            elif request.POST['action_p'] == 'true':
                action = 1
            elif request.POST['action_s'] == 'true':
                action = 2

            # game = game_manager.of(id)
            if debug:
                print(id, ": get game platform")
            platform.set_user_response(id, action)
            if debug:
                print(id, ": inserted action")

            platform.dump_log()

            # 等待
            while not platform.is_empty():
                pass
            time.sleep(1)  ## 有必要更大？

            history = History.get_record(id, 10)
            data = []
            for record in history:
                record_dict = {
                    "date": str(record.date),
                    "count": record.count
                }
                if id == record.id1:
                    record_dict['your_id'] = record.id1
                    record_dict['competitor_id'] = record.id2
                    record_dict['your_action'] = util.int2word(record.action1)
                    record_dict['competitor_action'] = util.int2word(record.action2)
                    record_dict['earn'] = util.earn(record.action1, record.action2)
                else:
                    record_dict['your_id'] = record.id2
                    record_dict['competitor_id'] = record.id1
                    record_dict['your_action'] = util.int2word(record.action2)
                    record_dict['competitor_action'] = util.int2word(record.action1)
                    record_dict['earn'] = util.earn(record.action2, record.action1)
                data.append(record_dict)
            if debug:
                print(data)
            time.sleep(1)
            if debug:
                print(json.dumps(data))

            # reward
            records = Record.objects \
                .filter(Q(id1=id) | Q(id2=id))
            rew = 0
            for r in records:
                rew += reward(r, id)

            ret = {
                'records': json.dumps(data),
                'counter': platform.counter + 1,  # 轮数
                'reward': rew
            }

            # In order to allow non-dict objects to be serialized set the safe parameter to False.
            return JsonResponse(ret)


def reward(record, id):
    if (record.id1 == id):
        return util.earn(record.action1, record.action2)
    else:
        return util.earn(record.action2, record.action1)
