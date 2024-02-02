from django.contrib.auth import login, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User # is this necessary? where is it used?
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
# The problem below in pycharm is wrong! the import works fine
from .models import Worker, Manager, Project, Task

from django.core import serializers
from django.template import loader
from datetime import datetime


from django.contrib import messages

from django.utils.http import urlsafe_base64_encode
from jwt.utils import force_bytes

from pymongo.auth import authenticate

from .forms import UserRegistrationForm


def index(request):
    projects_list = {"project1": {"task1": 150, "task2": 124}, "project2": {"task1": 130, "task2": 134},
                     "project3": {"task1": 5, "task2": 15}}
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


def open_screen(request):
    context = {
        'today_date': datetime.now().date()
    }
    return render(request, 'core/open_screen.html', context)


def signup_success(request):
    return render(request, 'core/signup_success.html')







def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Extract data from form
            usr_name = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')  # Assuming 'password1' is the field name
            f_name = form.cleaned_data.get('first_name')
            l_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            usr_type = form.cleaned_data.get('user_type')
            if usr_type == 'manager':
                # Create a new Manager
                manager = Manager(usr_name, pwd, f_name, l_name, email)
                # Save the Manager to the database
                manager.save()
            else:
                # Create a new Worker
                worker = Worker(usr_name, pwd, f_name, l_name, email)
                # Save the Worker to the database
                worker.save()
            return redirect('signup_success')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/sign_up.html', {'form': form})

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('user_home_screen')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/user_login.html', {'form': form})

def manager_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('manager_home_screen')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/manager_login.html', {'form': form})

from django.core.mail import send_mail
from django.contrib.auth.models import User
from .forms import ForgotPasswordForm

def user_forgot_password(request):
    email_sent = False
    email_not_sent = False
    email_not_found = False

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                try:
                    send_mail(
                        'Password reset',
                        'Here is the link to reset your password.',
                        'from@example.com',
                        [email],
                        fail_silently=False,
                    )
                    email_sent = True
                except:
                    email_not_sent = True
            else:
                email_not_found = True

    context = {
        'email_sent': email_sent,
        'email_not_sent': email_not_sent,
        'email_not_found': email_not_found,
    }

    return render(request, 'core/user_forgot_password.html', context)

def manager_forgot_password(request):
    email_sent = False
    email_not_sent = False
    email_not_found = False

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                try:
                    send_mail(
                        'Password reset',
                        'Here is the link to reset your password.',
                        'from@example.com',
                        [email],
                        fail_silently=False,
                    )
                    email_sent = True
                except:
                    email_not_sent = True
            else:
                email_not_found = True

    context = {
        'email_sent': email_sent,
        'email_not_sent': email_not_sent,
        'email_not_found': email_not_found,
    }

    return render(request, 'core/manager_forgot_password.html', context)