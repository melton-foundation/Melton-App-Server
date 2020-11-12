from django.urls import path

from posts import views

urlpatterns = [
    path("posts/", views.PostView.as_view({"get": "list"}), name="posts"),
    path("posts/<int:pk>", views.PostView.as_view({"get": "retrieve"}), name="post"),
]
