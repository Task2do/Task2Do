from django import forms
from django.forms import formset_factory
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.urls import reverse

from .forms import UserRegistrationForm, TaskEditForm
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
from .forms import ForgotPasswordForm, NewRequestForm, CreateProjectForm, EditProjectWorkersForm, TaskCreationForm, ManagerTaskEditForm, SubtaskDivisionForm, SubtaskForm, ProjectChangeForm, NewAssociationRequestForm, NewProjectRequestForm
from .models import Manager, Worker, Project, Task, PersonalData, Request
from django.db.models import Q
from .backend import ManagerBackend, WorkerBackend
from django.utils import timezone
from datetime import date

# import for request
from django.contrib.contenttypes.models import ContentType


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
from django.shortcuts import render
from .models import Request

@login_required(login_url='manager_login' or 'user_login')
def request_history(request):
    # Get the PersonalData instance for the current user
    personal_data = request.user.personal_data

    # Filter requests where the last sender is the current user's PersonalData
    requests_from_me = Request.objects.filter(last_sender=personal_data, is_active=False)

    # Filter requests where the last receiver is the current user's PersonalData
    requests_to_me = Request.objects.filter(last_receiver=personal_data, is_active=False)
    # Pass the requests to the template
    context = {'requests_from_me': requests_from_me, 'requests_to_me': requests_to_me}
    return render(request, 'core/request_history.html', context)


# needs to accept the form to add content to request or close it
from .forms import NewProjectRequestForm
from .models import Request, RequestContentHistory

@login_required(login_url='manager_login' or 'user_login')
def new_project_request(request):
    if request.method == 'POST':
        form = NewProjectRequestForm(request.POST, user=request.user)
        if form.is_valid():
            project = form.cleaned_data.get('project')
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')
            request_type = form.cleaned_data.get('request_type')

            new_request = Request.objects.create(
                type=request_type,
                last_sender=request.user.personal_data,
                last_receiver=project.lead.personal_data,
                header=title,
                is_active=True,
            )

            RequestContentHistory.objects.create(
                request=new_request,
                content=description
            )

            return redirect('requests_page')
    else:
        form = NewProjectRequestForm(user=request.user)
    return render(request, 'core/new_project_request.html', {'form': form})

# TODO add the request_to_view and user_id to the request
# change the data for forms(if accepted then associate with the reciever)
from django.shortcuts import get_object_or_404, render
from .models import Request, RequestContentHistory, Worker, Manager
@login_required(login_url='manager_login' or 'user_login')
def view_request_association(request, request_id):
    request_to_view = get_object_or_404(Request, id=request_id)

    if request.method == 'POST':
        if 'accept' in request.POST:
            # Check if a Worker object with the personal_data attribute set to request_to_view.last_sender exists
            if Worker.objects.filter(personal_data_id=request_to_view.last_sender.id).exists():
                worker = Worker.objects.get(personal_data_id=request_to_view.last_sender.id)
                manager = Manager.objects.get(personal_data_id=request_to_view.last_receiver.id)
                worker.managers.add(manager)
                worker.save()

                # Set the request to inactive
                request_to_view.is_active = False
                request_to_view.save()
                render(request, 'core/requests_page.html')

            elif Manager.objects.filter(personal_data_id=request_to_view.last_sender.id).exists():
                manager = Manager.objects.get(personal_data_id=request_to_view.last_sender.id)
                worker = Worker.objects.get(personal_data_id=request_to_view.last_receiver.id)
                worker.managers.add(manager)
                worker.save()

                request_to_view.is_active = False
                request_to_view.save()
                render(request, 'core/requests_page.html')

            else:
                return HttpResponse("Worker with the given personal data does not exist.")

        elif 'reject' in request.POST:
            # If the reject button was pressed, just set the request to inactive
            request_to_view.is_active = False
            request_to_view.save()
            render(request, 'core/requests_page.html')

    # Get the user_id from the request.user object
    user_id = request.user.id

    # Pass the Request object and user_id to the template
    context = {'request_to_view': request_to_view, 'user_id': user_id}
    return render(request, 'core/view_request_association.html', context)

# MANAGER views
def manager_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
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


# # Manager's projects
def specific_project_manager(request, project_id):
    project = Project.objects.get(id=project_id)
    return render(request, 'core/specific_project_manager.html', {'project': project})

@login_required(login_url='manager_login')
def specific_project_workers(request, project_id):
    project = Project.objects.get(id=project_id)
    workers = project.members.all()
    return render(request, 'core/specific_project_workers.html', {'project': project, 'workers': workers})

@login_required(login_url='manager_login')
def active_projects_manager(request):
    user_id = request.user.personal_data.id
    active_projects = Project.objects.filter(Q(is_active=True) & Q(lead__personal_data__id=user_id))
    context = {'active_projects': active_projects, 'now': timezone.now()}
    return render(request, 'core/active_projects_manager.html', context)


@login_required(login_url='manager_login')
def create_new_project(request):
    if request.method == 'POST':
        form = CreateProjectForm(request.POST, manager_id=request.user.personal_data.id)
        if form.is_valid():
            project = form.save(commit=False)
            project.lead = Manager.objects.get(personal_data__user=request.user)
            project.due_date = form.cleaned_data['due_date']
            project.save()
            project.members.set(form.cleaned_data['members'])  # Use set() method here
            project.save()

            return redirect('specific_project_manager', project_id=project.id)
    else:
        form = CreateProjectForm(manager_id=request.user.personal_data.id)
    return render(request, 'core/create_new_project.html', {'form': form})


@login_required(login_url='manager_login')
def project_history_manager(request):
    manager = Manager.objects.get(personal_data__user=request.user)
    projects = manager.lead_projects.all().filter(is_active=False, due_date__lt=timezone.now())
    projects_data = []
    for project in projects:
        num_tasks = project.tasks.count()
        num_workers = project.members.count()
        projects_data.append({
            'project': project,
            'num_tasks': num_tasks,
            'num_workers': num_workers,
        })
    return render(request, 'core/project_history_manager.html', {'projects_data': projects_data})


# # Manager's tasks
@login_required(login_url='manager_login')
def tasks_specific_project_manager(request, project_id):
    project = Project.objects.get(id=project_id)
    all_tasks = project.tasks.all()
    now = timezone.now().date()

    active_tasks = [task for task in all_tasks if task.is_active and task.due_date >= now]
    inactive_tasks = [task for task in all_tasks if not task.is_active and task.due_date >= now]
    active_tasks_past_deadline = [task for task in all_tasks if task.is_active and task.due_date < now]
    inactive_tasks_past_deadline = [task for task in all_tasks if not task.is_active and task.due_date < now]


    context = {
        'project': project,
        'active_tasks': active_tasks,
        'inactive_tasks': inactive_tasks,
        'active_tasks_past_deadline': active_tasks_past_deadline,
        'inactive_tasks_past_deadline': inactive_tasks_past_deadline,
    }

    return render(request, 'core/tasks_specific_project_manager.html', context)


def specific_task_manager(request, task_id):
    task = Task.objects.get(id=task_id)
    project = task.project_tasks.all().first()
    return render(request, 'core/specific_task_manager.html', {'task': task, 'project_id': project.id})


@login_required(login_url='manager_login')
def task_creation_screen_manager(request, project_id):
    if request.method == 'POST':
        form = TaskCreationForm(request.POST, project_id=project_id)
        if form.is_valid():
            task = form.save(commit=False)
            project = Project.objects.get(id=project_id)
            task.assigned_to = form.cleaned_data['assigned_to']
            task.due_date = form.cleaned_data['due_date']
            task.status = 'NOT STARTED'
            task.save() #TODO: Almog, there is a problem here with saving to the db
            project.tasks.add(task)
            project.save()
            return redirect('tasks_specific_project_manager', project_id=project_id)
    else:
        form = TaskCreationForm(project_id=project_id)
    return render(request, 'core/task_creation_screen_manager.html', {'form': form, 'project_id': project_id})


@login_required(login_url='manager_login')
def task_editing_screen_manager(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == 'POST':
        form = ManagerTaskEditForm(request.POST, instance=task)
        if 'save_changes' in request.POST:
            if form.is_valid():
                updated_task = form.save(commit=False)
                if updated_task.status == 'COMPLETED':
                    updated_task.is_active = False
                updated_task.save() # TODO: Almog, please check if this is the correct way to save the form
                return redirect('specific_task_manager', task_id=task.id)
        elif 'discard_changes' in request.POST:
            return redirect('specific_task_manager', task_id=task.id)
    else:
        form = ManagerTaskEditForm(instance=task)
    return render(request, 'core/task_editing_screen_manager.html', {'form': form, 'task_id': task_id})

@login_required(login_url='manager_login')
def edit_specific_project_workers(request, project_id):
    project = Project.objects.get(id=project_id)
    if request.method == 'POST':
        form = EditProjectWorkersForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('specific_project_workers', project_id=project_id)
    else:
        form = EditProjectWorkersForm(instance=project)
    return render(request, 'core/edit_specific_project_workers.html', {'form': form, 'project': project})

# # Manager's workers
@login_required(login_url='manager_login')
def workers_list_manager(request, manager_id):
    manager = Manager.objects.get(id=manager_id)
    workers = manager.workers.all()
    return render(request, 'core/workers_list_manager.html', {'workers': workers})


@login_required(login_url='manager_login')  # is this needed?
def worker_details_manager(request, worker_id):
    worker = Worker.objects.get(id=worker_id)
    return render(request, 'core/worker_details_manager.html', {'worker': worker})


@login_required(login_url='manager_login')
def change_project_manager(request, project_id):
    project = Project.objects.get(id=project_id)
    if request.method == 'POST':
        form = ProjectChangeForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('specific_project_manager', project_id=project.id)
    else:
        form = ProjectChangeForm(instance=project)
    return render(request, 'core/change_project_manager.html', {'form': form, 'project': project})


# # Manager's requests
@login_required
def requests_page(request):
    try:
        manager = Manager.objects.get(id=request.user.personal_data.id)
        user_type = 'manager'
    except Manager.DoesNotExist:
        user_type = 'worker'
    # Get the PersonalData instance for the current user
    personal_data = request.user.personal_data

    # Filter requests where the last sender is the current user's PersonalData
    requests_from_me = Request.objects.filter(last_sender=personal_data, is_active=True)

    # Filter requests where the last receiver is the current user's PersonalData
    requests_to_me = Request.objects.filter(last_receiver=personal_data, is_active=True)
    return render(request, 'core/requests_page.html',
                  {'requests_from_me': requests_from_me, 'requests_to_me': requests_to_me, 'user_type': user_type})


def new_association_request(request):
    if request.method == 'POST':
        form = NewAssociationRequestForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            user = User.objects.filter(username=username).first()
            if user:
                new_request = Request.objects.create(
                    type='ASOC',
                    last_sender=request.user.personal_data,
                    last_receiver=user.personal_data,
                    header='Association Request',
                    is_active=True,
                )
                new_content = RequestContentHistory.objects.create(
                    request=new_request,
                    content="This is a new association request."
                )
                return redirect('requests_page')
            else:
                form.add_error('username', 'This username does not exist.')
    else:
        form = NewAssociationRequestForm()
    return render(request, 'core/new_association_request.html', {'form': form, 'messages': messages})

def new_request_submission(request):
    user_type = 'manager' if isinstance(request.user, Manager) else 'worker'
    if request.method == 'POST':
        form = NewRequestForm(request.POST, user_type=user_type)
        if form.is_valid():
            # Extract form data
            type = form.cleaned_data.get('type')

            # Redirect based on the request type
            if type == 'association':
                return redirect('new_association_request')
            elif type == 'project':
                return redirect('new_project_request')
    else:
        form = NewRequestForm(user_type=user_type)
    return render(request, 'core/new_request_submission.html', {'form': form})


# USER views
def user_login(request):
    """
    This view function handles the user login process.
    If the request method is POST, it authenticates the user with the provided username and password.
    If the user is authenticated successfully, they are logged in and redirected to the user home screen.
    If the user is not authenticated, an error message is displayed.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The HTTP response.
    """
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


# # User's tasks
@login_required(login_url='user_login')
def task_history_user(request):
    worker_id = request.user.personal_data.id
    tasks = Task.objects.filter(Q(status='COMPLETED') | Q(status='CANCELED'), assigned_to=worker_id).order_by(
        '-due_date')
    return render(request, 'core/task_history_user.html', {'history_tasks': tasks})


@login_required(login_url='user_login')
def active_tasks_user(request):
    """
    This view function retrieves all active tasks assigned to the currently logged-in user.
    An active task is defined as a task that is not canceled and is marked as active.
    The tasks are then passed to the 'core/active_tasks_user.html' template to be displayed.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    user_id = request.user.personal_data.id
    active_tasks = Task.objects.filter(
        ~Q(status='CANCELED') & Q(is_active=True) & Q(assigned_to__personal_data__id=user_id))
    context = {'active_tasks': active_tasks}
    return render(request, 'core/active_tasks_user.html', context)


@login_required(login_url='user_login')
def specific_task_display_user(request, task_id):
    task = Task.objects.get(id=task_id, assigned_to__personal_data__id=request.user.personal_data.id)
    context = {'task': task, 'today_date': date.today()}
    return render(request, 'core/specific_task_display_user.html', context)


from .forms import TaskEditForm

@login_required(login_url='user_login')
def task_editing_screen_user(request, task_id):
    task = Task.objects.get(id=task_id, assigned_to__personal_data__id=request.user.personal_data.id)
    if request.method == 'POST':
        form = TaskEditForm(request.POST, instance=task)
        if 'save_changes' in request.POST:
            if form.is_valid():
                # form.save() TODO: Almog, please check if this is the correct way to save the form
                return redirect('specific_task_display_user', task_id=task.id)
        elif 'discard_changes' in request.POST:
            return redirect('specific_task_display_user', task_id=task.id)
        elif 'create_subtasks' in request.POST:
            return redirect('task_division_screen_user', task_id=task.id)
    else:
        form = TaskEditForm(instance=task)
    return render(request, 'core/task_editing_screen_user.html', {'form': form})

@login_required(login_url='user_login')
def task_division_screen_user(request, task_id):
    task = Task.objects.get(id=task_id, assigned_to__personal_data__id=request.user.personal_data.id)
    if request.method == 'POST':
        form = SubtaskDivisionForm(request.POST)
        if form.is_valid():
            num_subtasks = form.cleaned_data.get('num_subtasks')
            return redirect('create_subtasks', task_id=task.id, num_subtasks=num_subtasks)
    else:
        form = SubtaskDivisionForm()
    return render(request, 'core/task_division_screen_user.html', {'form': form, 'task': task})

@login_required(login_url='user_login')
def create_subtasks(request, task_id, num_subtasks):
    task = Task.objects.get(id=task_id, assigned_to__personal_data__id=request.user.personal_data.id)
    SubtaskFormSet = forms.formset_factory(SubtaskForm, extra=num_subtasks)
    if request.method == 'POST':
        formset = SubtaskFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                subtask = form.save(commit=False)
                subtask.parent_task = task
                subtask.due_date = task.due_date
                subtask.is_active = True
                subtask.assign_to = task.assigned_to

                # subtask.save() #TODO: Almog
            return redirect('specific_task_display_user', task_id=task.id)
    else:
        formset = SubtaskFormSet()
    return render(request, 'core/create_subtasks.html', {'formset': formset, 'task': task})

def subtask_definition_screen_user(request):
    pass


@login_required(login_url='user_login')
def upcoming_deadlines(request):
    """
    This view function retrieves all upcoming tasks assigned to the currently logged-in user.
    An upcoming task is defined as a task whose due date is in the future.
    The tasks are then passed to the 'core/upcoming_deadlines.html' template to be displayed.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The HTTP response.
    """
    now = timezone.now()
    upcoming_tasks = Task.objects.filter(due_date__gt=now,
                                         assigned_to__personal_data__id=request.user.personal_data.id).order_by(
        'due_date')
    context = {'upcoming_tasks': upcoming_tasks}
    return render(request, 'core/upcoming_deadlines.html', context)
