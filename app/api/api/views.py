from django.http import JsonResponse
from django.http import HttpResponseNotFound
from sentry_sdk import capture_message
from django.shortcuts import render

def error_400_view(request, exception):
    id = capture_message("Bad Request (400)", level="error")
    data = {"event_id": id,
            "code": 400,
            "title": "BAD REQUEST",
            "description": "The server cannot process the request due to a client error (e.g., malformed request syntax, invalid request message framing, or deceptive request routing)."}
    return render(request, data)

def error_403_view(request, exception):
    id = capture_message("Forbidden (403)", level="error")
    data = {"event_id": id,
            "code": 403,
            "title": "FORBIDDEN",
            "description": "The client has insufficient authentication credentials for the server to process this request."}
    return render(request, data)

def error_404_view(request, exception):
    id = capture_message("Not Found (404)", level="error")
    data = {"event_id": id,
            "code": 404, "title":
            "NOT FOUND", "description":
            "The server is not able to find the requested resource. AKA, Page Not Found."}
    return render(request, data)

def error_500_view(request):
    id = capture_message("Internal Server Error (500)", level="error")
    data = {"event_id": id,
            "code": 500,
            "title": "INTERNAL SERVER ERROR",
            "description": "The server encountered an unexpected condition that prevented it from fulfilling the request."}
    return render(request, data)

def index(request):
    json = {
        'name': 'Melton Foundation Server API',
        'version': '1.0.0',
        'Description': 'An API for Melton Foundation Fellows App'
    }
    return JsonResponse(json)