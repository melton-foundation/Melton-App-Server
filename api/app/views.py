from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the index page.")

def users(request):
    return HttpResponse("This is list of users")
