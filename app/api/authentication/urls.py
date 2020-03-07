from django.urls import path

from authentication import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('registration-status/', views.check_registration,
         name="check_registration"),
]
