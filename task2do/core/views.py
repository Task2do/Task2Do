from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import UserRegistrationForm
from django.http import HttpResponse, JsonResponse

from django.core import serializers
from django.template import loader
from datetime import datetime
from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.utils.http import urlsafe_base64_encode
from jwt.utils import force_bytes

from django.core.mail import send_mail
from django.contrib.auth.models import User
from .forms import ForgotPasswordForm
from .models import Manager, Worker, Project, Task, PersonalData, Request
from django.db.models import Q
from .backend import ManagerBackend, WorkerBackend


# Add more views for different functionalities like creating users, tasks, etc.

# should be helpful functions

# adding tasks and projects to the database
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


# general stuff
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
            password = form.cleaned_data.get('password')  # Adjust the field name if necessary
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            user_type = form.cleaned_data.get('user_type')
            birth_date = form.cleaned_data.get('birth_date')

            # Create Django User instance
            user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name,
                                            last_name=last_name)

            # Create PersonalData instance linked to the User
            personal_data = PersonalData.objects.create(user=user, b_date=birth_date)

            if user_type == 'manager':
                # Create a Manager instance
                manager = Manager.objects.create(personal_data=personal_data)
            else:  # Assuming the other option is 'worker'
                # Create a Worker instance
                worker = Worker.objects.create(personal_data=personal_data)

            return redirect('signup_success')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/sign_up.html', {'form': form})


def logout_view(request):
    if 'user_username' in request.session:
        del request.session['user_username']
    if 'manager_username' in request.session:
        del request.session['manager_username']
    return redirect('open_screen')  # Redirect to the open screen after logging out


# requests
def request_history(request):
    # Your view logic here
    return render(request, 'core/request_history.html')

#TODO: page needs request_to_view
# needs to accept the form to add content to request or close it
def specific_request_view(request, request_id):
    # Your view logic here
    return render(request, 'core/specific_request_view.html', {'request_id': request_id})


def view_request_association(request):
    # Your view logic here
    return render(request, 'core/view_request_association.html')


# manager stuff
def manager_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(user)
            login(request, user)
            return redirect('manager_home_screen')
        else:
            messages.error(request, 'Login failed. Please try again.')
    return render(request, 'core/manager_login.html')


def manager_forgot_password(request):
    email_sent = False
    email_not_sent = False
    email_not_found = False

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            manager = Manager.objects.filter(personal_data__user__email=email).first()
            if manager:
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


def manager_home_screen(request):
    return render(request, 'core/manager_home_screen.html')


def specific_project_manager(request, project_id):
    project = Project.objects.get(id=project_id)
    return render(request, 'core/specific_project_manager.html', {'project': project})


@login_required(login_url='manager_login')
def active_projects_manager(request):
    manager_id = request.user.personal_data.id
    active_projects = Project.objects.filter(is_active=True, lead_id=manager_id)

    projects_data = []
    for project in active_projects:
        num_tasks = project.tasks.count()
        num_workers = project.members.count()
        projects_data.append({
            'project': project,
            'num_tasks': num_tasks,
            'num_workers': num_workers,
        })

    context = {'projects_data': projects_data}
    return render(request, 'core/active_projects_manager.html', context)


def tasks_specific_project_manager(request, project_id):
    tasks = Task.objects.filter(project__id=project_id)
    return render(request, 'core/tasks_specific_project_manager.html', {'tasks': tasks})


def specific_task_manager(request, task_id):
    task = Task.objects.get(id=task_id)
    return render(request, 'core/specific_task_manager.html', {'task': task})


def workers_list_manager(request, manager_id):
    manager = Manager.objects.get(id=manager_id)
    workers = manager.workers.all()
    return render(request, 'core/workers_list_manager.html', {'workers': workers})


def worker_details_manager(request, worker_id):
    worker = Worker.objects.get(id=worker_id)
    return render(request, 'core/worker_details_manager.html', {'worker': worker})


@login_required(login_url='manager_login')
def requests_page(request):
    # Your view logic here
    requests_from_me = Request.objects.filter(last_sender=request.user.personal_data)
    requests_to_me = Request.objects.filter(last_reciever=request.user.personal_data)

    return render(request, 'core/requests_page.html',
                  {'requests_from_me': requests_from_me, 'requests_to_me': requests_to_me})


def new_association_request_manager(request):
    # Your view logic here
    return render(request, 'core/new_association_request_manager.html')


def project_history_manager(request):
    # Your view logic here
    return render(request, 'core/project_history_manager.html')


# user stuff
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user, backend='core.backend.WorkerBackend')
            return redirect('user_home_screen')
        else:
            messages.error(request, 'Login failed. Please try again.')
    return render(request, 'core/user_login.html')


def user_forgot_password(request):
    email_sent = False
    email_not_sent = False
    email_not_found = False

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = Worker.objects.filter(personal_data__user__email=email).first()
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


def user_home_screen(request):
    return render(request, 'core/user_home_screen.html')


def task_history_user(request):
    # Your view logic here
    # TODO : get tasks that were either completed or canceled of that user
    worker_id = request.user.personal_data.id  # Get the id of the currently logged-in manager
    tasks = Task.objects.filter(Q(status='COMPLETED') | Q(status='CANCELED'), assignee=worker_id)
    return render(request, 'core/task_history_user.html', {'history_tasks': tasks})


def task_creation_screen_manager(request):
    # Your view logic here
    return render(request, 'core/task_creation_screen_manager.html')


@login_required(login_url='user_login')
def active_tasks_user(request):
    user_id = request.user.personal_data.id
    active_tasks = Task.objects.filter(~Q(status='CANCELED') & Q(is_active=True), assigned_to=user_id)
    context = {'active_tasks': active_tasks}
    return render(request, 'core/active_tasks_user.html', context)


def specific_task_display_user(request, task_id):
    # Your view logic here
    return render(request, 'core/specific_task_display_user.html', {'task_id': task_id})


def task_division_screen_user(request):
    # Your view logic here
    return render(request, 'core/task_division_screen_user.html')


def new_request_submission(request):
    # Your view logic here
    return render(request, 'core/new_request_submission.html')


def subtask_definition_screen_user(request):
    # Your view logic here
    return render(request, 'core/subtask_definition_screen_user.html')


def upcoming_deadlines(request):
    # Your view logic here
    return render(request, 'core/upcoming_deadlines.html')


def new_association_request_submission_user(request):
    # Your view logic here
    return render(request, 'core/new_association_request_submission_user.html')


def task_editing_screen_user(request):
    # Your view logic here
    return render(request, 'core/task_editing_screen_user.html')
