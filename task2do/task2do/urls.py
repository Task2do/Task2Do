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
    path('sign_up/', views.signup_view, name='signup'),
    path('signup_success/', views.signup_success, name='signup_success'),
    # login
    path('user_login/', views.user_login, name='user_login'),
    path('manager_login/', views.manager_login, name='manager_login'),
    path('user_forgot_password/', views.user_forgot_password, name='user_forgot_password'),
    path('manager_forgot_password/', views.manager_forgot_password, name='manager_forgot_password'),
    # manager urls for home screen
    path('manager_home_screen/', views.manager_home_screen, name='manager_home_screen'),
    path('user_home_screen/', views.user_home_screen, name='user_home_screen'),
    path('active_projects/', views.active_projects, name='active_projects'),
    # path('view_project/<int:project_id>/', views.view_project, name='view_project'),
    path('workers_list_manager/<int:manager_id>/', views.workers_list_manager, name='workers_list_manager'),
    path('logout/', views.logout_view, name='logout'),
    path('view_request_project/<int:request_id>/', views.view_request_project, name='view_request_project'),
    path('request_history/', views.request_history, name='request_history'),
    path('project_history/', views.project_history, name='project_history'),
    path('task_creation_screen/<int:project_id>/', views.task_creation_screen, name='task_creation_screen'),
    # user urls for home screen
    path('active_tasks/', views.active_tasks, name='active_tasks'),
    path('upcoming_deadlines/', views.upcoming_deadlines, name='upcoming_deadlines'),
    path('my_requests/', views.requests_page, name='requests_page'),
    path('task_history/', views.task_history, name='task_history'),
    path('task_display_user/<int:task_id>/', views.task_display_user, name='task_display_user'),
    path('choose_subtasks_num/<int:task_id>/', views.choose_subtasks_num, name='choose_subtasks_num'),
    path('new_request_submission/', views.new_request_submission, name='new_request_submission'),
    path('view_request_association/<int:request_id>/', views.view_request_association, name='view_request_association'),
    path('task_editing_screen_user/', views.task_editing_screen_user, name='task_editing_screen_user'),
    path('create_new_project/', views.create_new_project, name='create_new_project'),
    path('view_project/<int:project_id>/', views.view_project, name='view_project'),
    path('project_tasks/<int:project_id>/', views.project_tasks, name='project_tasks'),
    path('task_display_manager/<int:task_id>/', views.task_display_manager, name='task_display_manager'),
    path('workers_list_manager/<int:manager_id>/', views.workers_list_manager, name='workers_list_manager'),
    path('worker_details/<int:worker_id>/', views.worker_details, name='worker_details'),
    path('edit_project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('task_editing_screen_user/<int:task_id>/', views.task_editing_screen_user, name='task_editing_screen_user'),
    path('create_subtasks/<int:task_id>/<int:num_subtasks>/', views.create_subtasks, name='create_subtasks'),
    path('project_workers/<int:project_id>/', views.project_workers, name='project_workers'),
    path('edit_project_workers/<int:project_id>/', views.edit_project_workers, name='edit_project_workers'),
    path('new_association_request/', views.new_association_request, name='new_association_request'),
    path('task_editing_screen_manager/<int:task_id>/', views.task_editing_screen_manager, name='task_editing_screen_manager'),
    path('new_project_request/', views.new_project_request, name='new_project_request'),

]

