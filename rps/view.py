from django.http import HttpResponse
from django.template import loader


def index(request):
    template = loader.get_template('rps/index.html')
    context = {}
    return HttpResponse(template.render(context, request))


def play(request):
    id = request.POST['id']
    print("id: ", id)

    template = loader.get_template('rps/play.html')
    context = {"id": id}
    return HttpResponse(template.render(context, request))
