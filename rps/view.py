from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .models import Record
from django.utils import timezone
from django.http import JsonResponse
from .control.game import GameManager
import json
import time

game_manager = GameManager()


def index(request):
    context = {}
    return render(request, 'rps/index.html', context)


def play(request):
    id = request.POST['id']
    print("id: ", id)

    # create a game for this player
    context = {"id": id}

    return render(request, 'rps/play.html', context)


def handon(request):
    id = request.POST['id']
    data = {"info": "handon return"}
    print(request.POST)

    if request.method == 'POST':
        if request.is_ajax():
            action = -1
            print(type(request.POST['action_r']))
            if request.POST['action_r'] == 'true':
                action = 0
            elif request.POST['action_p'] == 'true':
                action = 1
            elif request.POST['action_s'] == 'true':
                action = 2

            game = game_manager.of(id)
            print(id, ": get game platform")
            game.insert(id, action)
            game.wait_competitor_result()
            print(id, ": inserted action")

            history = game.history(10)
            data = []
            for record in history:
                record_dict = {
                    "id1": record.id1,
                    "id2": record.id2,
                    "action1": record.action1,
                    "action2": record.action2,
                    "date": str(record.date),
                    "count": record.count
                }
                data.append(record_dict)
            print(data)
            time.sleep(1)
            print(json.dumps(data))

            ret = {
                'records': json.dumps(data)
            }

            # In order to allow non-dict objects to be serialized set the safe parameter to False.
            return JsonResponse(ret)
