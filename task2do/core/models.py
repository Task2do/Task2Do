from django.db import models
from django.db.models.functions import datetime
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password



# global variables
# the type of the request
REQUEST_TYPE = [
    ('JOIN', 'join'),  # when joining a project
    ('LEAVE', 'leave'),  # when leaving a project
    ('CREATE', 'create'),  # when creating a task
    ('UPDATE', 'update'),  # when updating a task
    ('FINISH', 'finish'),  # when finishing a task
]

STATUS_CHOICES = [
    ('NOT STARTED', 'Not Started'),
    ('IN PROGRESS', 'In Progress'),
    ('ADVANCED', 'Advanced'),  # when the task is advanced
    ('ON HOLD', 'On Hold'),  # when the task is on hold
    ('CANCELED', 'Canceled'),  # when the task is canceled
    ('BLOCKED', 'Blocked'),  # when the task is blocked
    ('COMPLETED', 'Completed'),
]


class PersonalData(models.Model):
    '''
    PersonalData model representing personal data of a user.
    '''
    user_name = models.CharField(max_length=75, primary_key=True)  # this the PK of the model
    password = models.CharField(max_length=75)  # must have
    first_name = models.CharField(max_length=30)  # must have
    last_name = models.CharField(max_length=75)  # must have
    email = models.EmailField()  # must have
    b_date = models.DateField()  # not must have


class Worker(models.Model):
    personal_data = models.OneToOneField(PersonalData, on_delete=models.CASCADE)
    tasks = models.ManyToManyField('Task', related_name='worker_tasks')
    last_login = models.DateTimeField(null=True)


class Manager(models.Model):
    personal_data = models.OneToOneField(PersonalData, on_delete=models.CASCADE)
    lead_projects = models.ManyToManyField('Project', related_name='manager_projects')
    last_login = models.DateTimeField(null=True)


class Request(models.Model):
    '''
    Request model representing a request from a user to join a project.
    '''
    request_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=10, choices=REQUEST_TYPE)
    # using the usr _id
    last_sender = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='sent_requests')
    last_receiver = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='reveiver')  # using the usr _id
    content = models.TextField(max_length=2048)
    header = models.CharField(max_length=128)


class Project(models.Model):
    """
       Project model representing a team project with a name, a lead, and members.
       """
    _id = models.AutoField(primary_key=True, default=-1)
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    lead = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name="projects_leader")
    members = models.ManyToManyField(Worker, related_name='member_projects')
    tasks = models.ManyToManyField('Task', related_name='project_tasks')


class Task(models.Model):
    """
       Task model representing an individual task within a project.
    """
    _id = models.AutoField(primary_key=True, default=-1)
    title = models.CharField(max_length=64)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Not Started')
    author = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='authored_tasks')
    assignee = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_tasks')
    is_active = models.BooleanField(default=True)

