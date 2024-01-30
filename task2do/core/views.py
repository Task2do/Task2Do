from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from .models import Worker, Manager, Project, Task
from django.core import serializers
from django.template import loader

def index(request):
    projects_list ={"project1":{"task1":150,"task2":124},"project2":{"task1":130,"task2":134},"project3":{"task1":5,"task2":15}}
    template = loader.get_template("core/templates/core/user.html")
    context = {
        "projects": projects_list,
    }
    return HttpResponse(template.render(context, request))

# Add more views for different functionalities like creating users, tasks, etc.


def projects_list(request):
    """
    View to list all projects with their related tasks.
    Each project includes the name, description, and a list of tasks.
    Each task includes the title, description, due date, and assignee.
    """
    projects = Project.objects.all().prefetch_related('tasks__assignee')
    projects_data = []

    for project in projects:
        tasks_data = []
        for task in project.tasks.all():
            tasks_data.append({
                'title': task.title,
                'description': task.description,
                'due_date': task.due_date,
                'assignee': {
                    'id': task.assignee.id if task.assignee else None,
                    'username': task.assignee.user.username if task.assignee else None,
                    # Add other user details if necessary
                }
            })

        projects_data.append({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'is_active': project.is_active,
            'tasks': tasks_data,
            'lead': {
                'id': project.lead.id,
                'username': project.lead.user.username,
                # Add other user details if necessary
            },
            'members': [
                {
                    'id': member.id,
                    'username': member.user.username,
                    # Add other user details if necessary
                } for member in project.members.all()
            ],
        })

    return JsonResponse({'projects': projects_data})

def users_list(request):
    """
    View to list all users with their related projects.
    Includes both projects led by the user and projects where the user is a member.
    """
    users = Worker.objects.all().prefetch_related('lead_projects', 'member_projects')
    users_data = []

    for user in users:
        user_data = {
            'id': user.id,
            'username': user.user.username,
            'first_name': user.user.first_name,
            'last_name': user.user.last_name,
            'email': user.user.email,
            'lead_projects': [
                {
                    'id': project.id,
                    'name': project.name,
                    # Add other project details if necessary
                } for project in user.lead_projects.all()
            ],
            'member_projects': [
                {
                    'id': project.id,
                    'name': project.name,
                    # Add other project details if necessary
                } for project in user.member_projects.all()
            ],
        }
        users_data.append(user_data)

    return JsonResponse({'users': users_data})
