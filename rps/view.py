from django.http import HttpResponse
from django.template import loader
from .control.game import Game
from django.shortcuts import render
from .models import Record
from django.utils import timezone
import time

games = {}


def index(request):
    context = {}
    return render(request, 'rps/index.html', context)


def play(request):
    id = request.POST['id']
    print("id: ", id)

    # create a game for this player
    games['id'] = Game('id')
    context = {"id": id}

    return render(request, 'rps/play.html', context)


def handon(request):
    id = request.POST['id']
    action = request.POST.getlist('action')

    record = Record()
    record.user_id = str(id)
    record.user_action = int(action[0])
    record.competitor_id = "competitor-" + str(id)
    record.competitor_action = (record.user_action + 1) % 3
    record.date = timezone.now()

    old_record_list = Record.objects.order_by('-date')

    if len(old_record_list) == 0:
        record.count = 1
    else:
        record.count = old_record_list[0].count + 1

    record.save()

    record_list = Record.objects.filter(user_id=id).order_by('-date')[:10]
    context = {'history_list': record_list}
    return render(request, 'rps/play.html', context)
