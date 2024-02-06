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


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.open_screen, name='open_screen'),

    #signup
    path('signup/', views.signup_view, name='signup'),
    path('signup_success/', views.signup_success, name='signup_success'),
    # login
    path('user_login/', views.user_login, name='user_login'),
    path('manager_login/', views.manager_login, name='manager_login'),
    path('user_forgot_password/', views.user_forgot_password, name='user_forgot_password'),
    path('manager_forgot_password/', views.manager_forgot_password, name='manager_forgot_password'),
    # manager urls for home screen
    path('manager_home_screen/', views.manager_home_screen, name='manager_home_screen'),
    path('user_home_screen/', views.user_home_screen, name='user_home_screen'),
    path('active_projects_manager/', views.active_projects_manager, name='active_projects_manager'),
    path('specific_project_manager/<int:project_id>/', views.specific_project_manager, name='specific_project_manager'),
    path('tasks_specific_project_manager/<int:project_id>/', views.tasks_specific_project_manager, name='tasks_specific_project_manager'),
    path('specific_task_manager/<int:task_id>/', views.specific_task_manager, name='specific_task_manager'),
    path('workers_list_manager/', views.workers_list_manager, name='workers_list_manager'),
    path('worker_details_manager/<int:worker_id>/', views.worker_details_manager, name='worker_details_manager'),
    path('logout/', views.logout_view, name='logout'),
    path('specific_request_view/<int:request_id>/', views.specific_request_view, name='specific_request_view'),
    path('view_request_association/', views.view_request_association, name='view_request_association'),
    path('request_history/', views.request_history, name='request_history'),
    path('project_history_manager/', views.project_history_manager, name='project_history_manager'),
    path('task_creation_screen_manager/', views.task_creation_screen_manager, name='task_creation_screen_manager'),
    # user urls for home screen
    path('active_tasks_user/', views.active_tasks_user, name='active_tasks_user'),
    path('upcoming_deadlines/', views.upcoming_deadlines, name='upcoming_deadlines'),
    path('my_requests/', views.requests_page, name='requests_page'),
    path('task_history_user/', views.task_history_user, name='task_history_user'),
    path('specific_task_display_user/<int:task_id>/', views.specific_task_display_user, name='specific_task_display_user'),
    path('task_division_screen_user/', views.task_division_screen_user, name='task_division_screen_user'),
    path('new_request_submission/', views.new_request_submission, name='new_request_submission'),
    path('subtask_definition_screen_user/', views.subtask_definition_screen_user, name='subtask_definition_screen_user'),

    path('task_editing_screen_user/', views.task_editing_screen_user, name='task_editing_screen_user'),
    path('create_new_project/', views.create_new_project, name='create_new_project'),
    path('active_projects_manager/', views.active_projects_manager, name='active_projects_manager'),
    path('specific_project_manager/<int:project_id>/', views.specific_project_manager, name='specific_project_manager'),
    path('tasks_specific_project_manager/<int:project_id>/', views.tasks_specific_project_manager, name='tasks_specific_project_manager'),
    path('specific_task_manager/<int:task_id>/', views.specific_task_manager, name='specific_task_manager'),
    path('workers_list_manager/<int:manager_id>/', views.workers_list_manager, name='workers_list_manager'),
    path('worker_details_manager/<int:worker_id>/', views.worker_details_manager, name='worker_details_manager'),
    path('change_project_manager/<int:project_id>/', views.change_project_manager, name='change_project_manager'),
]

