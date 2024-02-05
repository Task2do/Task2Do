from django.db import models
from django.db.models.functions import datetime
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
# Learn more abt GenericForeignKey: https://docs.djangoproject.com/en/stable/ref/contrib/contenttypes/#generic-relations
from django.contrib.contenttypes.models import ContentType


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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personal_data')
    b_date = models.DateField() # addional by Task2Do



class Worker(models.Model):
    personal_data = models.OneToOneField(PersonalData, on_delete=models.CASCADE)
    last_login = models.DateTimeField(null=True)


class Manager(models.Model):
    personal_data = models.OneToOneField(PersonalData, on_delete=models.CASCADE)
    last_login = models.DateTimeField(null=True)


class Request(models.Model):
    '''
    Request model representing a request from a user to join a project.
    '''
    type = models.CharField(max_length=10, choices=REQUEST_TYPE)

    # Setting up GenericForeignKey for the sender
    sender_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='request_senders',
                                            limit_choices_to={'model__in': ('worker', 'manager')})
    sender_object_id = models.PositiveIntegerField()
    last_sender = GenericForeignKey('sender_content_type', 'sender_object_id')

    # Setting up GenericForeignKey for the receiver
    receiver_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='request_receivers',
                                              limit_choices_to={'model__in': ('worker', 'manager')})
    receiver_object_id = models.PositiveIntegerField()
    last_receiver = GenericForeignKey('receiver_content_type', 'receiver_object_id')

    is_active = models.BooleanField(default=True)

    header = models.CharField(max_length=128)
    # For tracking the history of content
    contents = GenericRelation('RequestContentHistory')


class RequestContentHistory(models.Model):
    request = models.ForeignKey(Request, related_name='content_history', on_delete=models.CASCADE)
    content = models.TextField(max_length=2048)
    updated_at = models.DateTimeField(auto_now_add=True)


class Task(models.Model):
    """
       Task model representing an individual task within a project.
    """
    title = models.CharField(max_length=64)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Not Started')
    is_active = models.BooleanField(default=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': ('worker', 'manager')})
    object_id = models.PositiveIntegerField()
    author = GenericForeignKey('content_type', 'object_id')
    assigned_to = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='assigned_tasks', default=None)
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_tasks')


class Project(models.Model):
    """
       Project model representing a team project with a name, a lead, and members.
       """
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    lead = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name="lead_projects")
    members = models.ManyToManyField(Worker, related_name='projects')
    tasks = models.ManyToManyField(Task, related_name='project_tasks')




