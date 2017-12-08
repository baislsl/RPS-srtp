from django.http import HttpResponse
from django.template import loader
from .control.game import Game
from django.shortcuts import render

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
    context = {}

    return render(request, 'rps/play.html', context)
