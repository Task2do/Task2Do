import pytest
import os
from django.contrib.auth.models import User
from .models import Manager, Worker, Project, Task, PersonalData, Request
from .forms import UserRegistrationForm, TaskCreationForm, CreateProjectForm
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

# Set the Django settings module environment variable
os.environ['DJANGO_SETTINGS_MODULE'] = 'task2do.task2do.settings'


@pytest.mark.django_db
def test_user_registration_form_with_valid_data():
    form = UserRegistrationForm(data={
        'username': 'testuser',
        'password': 'testpassword123',
        'email': 'testuser@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'birth_date': '2000-01-01',
        'user_type': 'worker'
    })
    assert form.is_valid()


@pytest.mark.django_db
def test_user_registration_form_with_invalid_data():
    form = UserRegistrationForm(data={
        'username': 'testuser',
        'password': 'test',  # password too short
        'email': 'testuser@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'birth_date': '2000-01-01',
        'user_type': 'worker'
    })
    assert not form.is_valid()


@pytest.mark.django_db
def test_task_creation_form_with_valid_data():
    worker = Worker.objects.create(personal_data=PersonalData.objects.create(
        user=User.objects.create_user(username='testuser', password='testpassword123')))
    form = TaskCreationForm(data={
        'title': 'Test Task',
        'assigned_to': worker.id,
        'due_date': '2022-12-31',
        'description': 'This is a test task'
    }, project_id=1)
    assert form.is_valid()


@pytest.mark.django_db
def test_task_creation_form_with_invalid_data():
    form = TaskCreationForm(data={
        'title': '',  # empty title
        'assigned_to': 1,
        'due_date': '2022-12-31',
        'description': 'This is a test task'
    }, project_id=1)
    assert not form.is_valid()


@pytest.mark.django_db
def test_create_new_project_form_with_valid_data():
    form = CreateProjectForm(data={
        'name': 'Test Project',
        'description': 'This is a test project',
        'members': [],
        'due_date': '2022-12-31'
    }, manager_id=1)
    assert form.is_valid()


@pytest.mark.django_db
def test_create_new_project_form_with_invalid_data():
    form = CreateProjectForm(data={
        'name': '',  # empty name
        'description': 'This is a test project',
        'members': [],
        'due_date': '2022-12-31'
    }, manager_id=1)
    assert not form.is_valid()


@pytest.mark.django_db
def test_user_login_with_valid_credentials():
    User.objects.create_user(username='testuser', password='testpassword123')
    client = Client()
    response = client.post(reverse('user_login'), {'username': 'testuser', 'password': 'testpassword123'})
    assert response.status_code == 302  # should redirect to home screen


@pytest.mark.django_db
def test_user_login_with_invalid_credentials():
    User.objects.create_user(username='testuser', password='testpassword123')
    client = Client()
    response = client.post(reverse('user_login'), {'username': 'testuser', 'password': 'wrongpassword'})
    assert 'Login failed. Please try again.' in response.content.decode()


@pytest.mark.django_db
def test_task_creation_with_future_due_date():
    worker = Worker.objects.create(personal_data=PersonalData.objects.create(
        user=User.objects.create_user(username='testuser', password='testpassword123')))
    project = Project.objects.create(name='Test Project', description='This is a test project',
                                     lead=Manager.objects.create(personal_data=PersonalData.objects.create(
                                         user=User.objects.create_user(username='testmanager',
                                                                       password='testpassword123'))))
    task = Task.objects.create(title='Test Task', description='This is a test task',
                               due_date=timezone.now() + timedelta(days=1), assigned_to=worker)
    project.tasks.add(task)
    assert task in project.tasks.all()


@pytest.mark.django_db
def test_task_creation_with_past_due_date():
    worker = Worker.objects.create(personal_data=PersonalData.objects.create(
        user=User.objects.create_user(username='testuser', password='testpassword123')))
    project = Project.objects.create(name='Test Project', description='This is a test project',
                                     lead=Manager.objects.create(personal_data=PersonalData.objects.create(
                                         user=User.objects.create_user(username='testmanager',
                                                                       password='testpassword123'))))
    task = Task.objects.create(title='Test Task', description='This is a test task',
                               due_date=timezone.now() - timedelta(days=1), assigned_to=worker)
    project.tasks.add(task)
    assert task in project.tasks.all()
