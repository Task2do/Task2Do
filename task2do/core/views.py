from django.http import JsonResponse
from .models import User, Project, Task #import everything from models.py
from django.shortcuts import render

from django.http import HttpResponse

from django.http import HttpResponse
from django.template import loader

def index(request):
    projects_list ={"project1":{"task1":150,"task2":124},"project2":{"task1":130,"task2":134},"project3":{"task1":5,"task2":15}}
    template = loader.get_template("core/templates/core/user.html")
    context = {
        "projects": projects_list,
    }
    return HttpResponse(template.render(context, request))

# Add more views for different functionalities like creating users, tasks, etc.
