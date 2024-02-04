from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import Worker, Manager, Project, Task
from .forms import UserRegistrationForm
from django.http import HttpResponse, JsonResponse

from django.core import serializers
from django.template import loader
from datetime import datetime


from django.contrib import messages

from django.utils.http import urlsafe_base64_encode
from jwt.utils import force_bytes

from django.core.mail import send_mail
from django.contrib.auth.models import User
from .forms import ForgotPasswordForm
from .models import Manager, Worker, Project, Task




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
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')  # Assuming 'password1' is the field name
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            user_type = form.cleaned_data.get('user_type')
            birth_date = form.cleaned_data.get('birth_date')

            if user_type == 'manager':
                # Check if the email already exists for the manager user type
                if Manager.objects.filter(email=email).exists():
                    messages.error(request, 'Email already exists for this user type. Please choose another one.')
                    return redirect('signup')
                # Create a new Manager
                id = Manager.objects.count() + 1
                manager = Manager.objects.create(user_name=username, password=password, first_name=first_name, last_name=last_name,
                                       email=email, b_date=birth_date, _id=id)
                # Save the Manager to the database
                manager.save()

            else:  # Assuming the other option is 'worker'
                # Check if the email already exists for the worker user type
                if Worker.objects.filter(email=email).exists():
                    messages.error(request, 'Email already exists for this user type. Please choose another one.')
                    return redirect('signup')
                # Create a new Worker
                id = Worker.objects.count() + 1
                worker = Worker.objects.create(user_name=username, password=password, first_name=first_name, last_name=last_name,
                                      email=email, b_date=birth_date, _id=id)
                # Save the Worker to the database
                worker.save()

            return redirect('signup_success')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/sign_up.html', {'form': form})




from django.contrib.auth import authenticate, login
from django.contrib import messages


from .backend import ManagerBackend, WorkerBackend

def manager_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        be = ManagerBackend()
        manager = be.authenticate(request=request, username=username, password=password)
        if manager is not None:
            request.session['manager_username'] = manager.user_name
            return redirect('manager_home_screen')
        else:
            messages.error(request, 'Login failed. Please try again.')
    return render(request, 'core/manager_login.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        be = WorkerBackend()
        user = be.authenticate(request=request, username=username, password=password)
        if user is not None:
            request.session['user_username'] = user.user_name
            return redirect('user_home_screen')
        else:
            messages.error(request, 'Login failed. Please try again.')
    return render(request, 'core/user_login.html')


def logout_view(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'manager_id' in request.session:
        del request.session['manager_id']
    return redirect('open_screen')  # Redirect to the open screen after logging out

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

#adding tasks and projects to the database
def add_task_to_worker(request, worker_id, task_id):
    worker = Worker.objects.get(_id=worker_id)
    task = Task.objects.get(id=task_id)
    worker.tasks.add(task)
    worker.save()

def add_project_to_manager(request, manager_id, project_id):
    manager = Manager.objects.get(_id=manager_id)
    project = Project.objects.get(id=project_id)
    manager.lead_projects.add(project)
    manager.save()

def manager_home_screen(request):
    return render(request, 'core/manager_home_screen.html')

def user_home_screen(request):
    return render(request, 'core/user_home_screen.html')