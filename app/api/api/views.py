from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import (PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.http import JsonResponse
from django.shortcuts import render
from sentry_sdk import capture_message


def error_400_view(request, exception):
    sentry_id = capture_message("Bad Request (400)", level="error")
    data = {"event_id": sentry_id,
            "code": 400,
            "title": "BAD REQUEST",
            "description": "The server cannot process the request due to a client error (e.g., malformed request syntax, invalid request message framing, or deceptive request routing)."}
    return JsonResponse(data, status=400)


def error_403_view(request, exception):
    sentry_id = capture_message("Forbidden (403)", level="error")
    data = {"event_id": sentry_id,
            "code": 403,
            "title": "FORBIDDEN",
            "description": "The client has insufficient authentication credentials for the server to process this request."}
    return JsonResponse(data, status=403)


def error_404_view(request, exception):
    sentry_id = capture_message("Not Found (404)", level="error")
    data = {"event_id": sentry_id,
            "code": 404, "title":
            "NOT FOUND", "description":
            "The server is not able to find the requested resource. AKA, Page Not Found."}
    return JsonResponse(data, status=404)


def error_500_view(request):
    sentry_id = capture_message("Internal Server Error (500)", level="error")
    data = {"event_id": sentry_id,
            "code": 500,
            "title": "INTERNAL SERVER ERROR",
            "description": "The server encountered an unexpected condition that prevented it from fulfilling the request."}
    return JsonResponse(data, status=500)


def index(request):
    json = {
        'name': 'Melton Foundation Server API',
        'version': '1.0.0',
        'Description': 'An API for Melton Foundation Fellows App'
    }
    return JsonResponse(json)

def docs(request):
    return render(request, 'openapi/index.html')


class AdminViewContext(object):
    def get_context_data(self, **kw):
        # super will automatically call the right Form class for each view
        context = super().get_context_data(**kw)
        context['site_header'] = settings.SITE_HEADER
        context['site_title'] = settings.SITE_TITLE
        return context


class AdminPasswordResetView(AdminViewContext, PasswordResetView):
    pass


class AdminPasswordResetDoneView(AdminViewContext, PasswordResetDoneView):
    pass


class AdminPasswordResetCompleteView(AdminViewContext, PasswordResetCompleteView):
    pass


class AdminPasswordResetConfirmView(AdminViewContext, PasswordResetConfirmView):
    pass
