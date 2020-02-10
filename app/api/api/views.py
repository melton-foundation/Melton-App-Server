from django.http import JsonResponse


def index(request):
    json = {
        'name': 'Melton Foundation Server API',
        'version': '1.0.0',
        'Description': 'An API for Melton Foundation Fellows App'
    }
    return JsonResponse(json)