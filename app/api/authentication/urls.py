from django.urls import path

from authentication import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("registration-status/", views.check_registration, name="check_registration"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("login/", views.login, name="login"),
    path("users/", views.UsersView.as_view({"get": "list"}), name="users"),
    path("users/<int:pk>", views.UsersView.as_view({"get": "retrieve"}), name="user"),
]
