from django.db import models


class Worker(models.Model):
    # Additional user fields if needed
    # user = models.OneToOneField(, on_delete=models.CASCADE)
    pass
class Manager(models.Model):
    pass
class Project(models.Model):
    """
       Project model representing a team project with a name, a lead, and members.
       """
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    lead = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='lead_projects')
    members = models.ManyToManyField(Worker, related_name='member_projects')

    def __str__(self):
        return self.name

class Task(models.Model):
    """
       Task model representing an individual task within a project.
       """
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=50)
    author = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='authored_tasks')
    assignee = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_tasks')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
