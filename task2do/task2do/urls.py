"""
URL configuration for task2do project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from core import views
# The problem above in pycharm is wrong! the import works fine


urlpatterns = [
    path('admin/', admin.site.urls),
    path('projects/', views.projects_list, name='project-list'),
    path('', views.open_screen, name='open_screen'),
    path('users/', views.users_list, name='users-list'),
    path('signup/', views.signup_view, name='signup'),
    path('signup/success/', views.signup_success, name='signup-success'),
]

