from django.http import JsonResponse
from .models import User, Project, Task
from django.shortcuts import render

def project_list(request):
    projects = Project.objects.all().values()
    return JsonResponse(list(projects), safe=False)

# Add more views for different functionalities like creating users, tasks, etc.
