from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Additional user fields if needed
    pass

class Project(models.Model):
    name = models.CharField(max_length=100)
    lead = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lead_projects')
    members = models.ManyToManyField(User, related_name='member_projects')

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tasks')
    due_date = models.DateField()
