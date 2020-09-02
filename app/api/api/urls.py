"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from api import views

handler400 = 'api.views.error_400_view'
handler403 = 'api.views.error_403_view'
handler404 = 'api.views.error_404_view'
handler500 = 'api.views.error_500_view'

urlpatterns = [
    path('admin/password_reset/', views.AdminPasswordResetView.as_view(), name='admin_password_reset'),
    path('admin/password_reset/done/', views.AdminPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.AdminPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.AdminPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin/', admin.site.urls),
    path('markdownx/', include('markdownx.urls')),
    path('api/', views.index),
    path('api/', include('authentication.urls')),
    path('api/', include('store.urls')),
    path('api/', include('posts.urls'))
]
