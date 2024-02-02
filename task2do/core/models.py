from django.db import models
from django.db.models.functions import datetime

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

    def __init__(self, usr_name, pwd, f_name, l_name, email, b_date=None):
        self.user_name = usr_name
        self.password = pwd
        self.first_name = f_name
        self.last_name = l_name
        self.email = email
        self.b_date = b_date

    def update_password(self, new_password):
        self.password = new_password
        self.save()

    def update_email(self, new_email):
        self.email = new_email
        self.save()

    def update_b_date(self, new_b_date):
        self.b_date = new_b_date
        self.save()

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def is_birthday_today(self):
        return self.b_date == datetime.datetime.today()

    def delete_user(self):
        self.delete()


class Worker(PersonalData):
    personaldata_ptr = models.OneToOneField(PersonalData, on_delete=models.CASCADE,
                                            parent_link=True, default=-1)
    _id = models.AutoField(primary_key=True, default=-1)
    tasks = models.ManyToManyField('Task', related_name='worker_tasks')

    def __init__(self, usr_name, pwd, f_name, l_name, email, b_date=None):
        super().__init__(usr_name, pwd, f_name, l_name, email, b_date)
        # create a uniqe id for the worker base on the workers sql db table
        self._id = Worker.objects.count() + 1
        self.tasks = []
        # insert the worker to the workers table
        Worker.objects.create(user_name=usr_name, password=pwd, first_name=f_name, last_name=l_name, email=email,
                              b_date=b_date)



    def add_task(self, task):
        self.tasks.append(task)
        self.save()

    def remove_task(self, task):
        self.tasks.remove(task)
        self.save()

    def update_task(self, task):
        self.save()

    def assign_task(self, task):
        self.tasks.add(task)
        self.save()

    def unassign_task(self, task):
        self.tasks.remove(task)
        self.save()

    def get_assigned_tasks(self):
        return self.tasks.all()

    def get_completed_tasks(self):
        return self.tasks.filter(status='COMPLETED')

    def get_active_tasks(self):
        return self.tasks.filter(is_active=True)

    def delete_worker(self):
        self.delete()

class Manager(PersonalData):
    # the manager is a subclass of the PersonalData class. This is a one-to-one relationship.
    personaldata_ptr = models.OneToOneField(PersonalData, on_delete=models.CASCADE,
                                            parent_link=True, default=-1)
    _id = models.AutoField(primary_key=True, default=-1)
    lead_projects = models.ManyToManyField('Project', related_name='manager_projects')

    def __init__(self, usr_name, pwd, f_name, l_name, email, b_date=None):
        super.__init__(usr_name, pwd, f_name, l_name, email, b_date)
        # create a uniqe id for the manager base on the managers sql db table
        self._id = Manager.objects.count() + 1
        self.lead_projects = []
        # insert the manager to the managers table
        Manager.objects.create(user_name=usr_name, password=pwd, first_name=f_name, last_name=l_name, email=email,
                               b_date=b_date)

    def assign_project(self, project):
        self.lead_projects.add(project)
        self.save()

    def unassign_project(self, project):
        self.lead_projects.remove(project)
        self.save()

    def get_assigned_projects(self):
        return self.lead_projects.all()

    def get_active_projects(self):
        return self.lead_projects.filter(is_active=True)

    def delete_manager(self):
        self.delete()

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

    def __init__(self, type, last_sender, last_receiver, content, header):
        self.type = type
        self.last_sender = last_sender
        self.last_receiver = last_receiver
        self.content = content
        self.header = header
        # insert the request to the requests table
        Request.objects.create(type=type, last_sender=last_sender, last_receiver=last_receiver, content=content,
                               header=header)
    def update_content(self, new_content):
        self.content = new_content
        self.save()

    def update_header(self, new_header):
        self.header = new_header
        self.save()

    def delete_request(self):
        self.delete()

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

    def __init__(self, name, description, lead):
        self.name = name
        self.description = description
        self.lead = lead
        self.members = []
        self.tasks = []
        # create a uniqe id for the project base on the projects sql db table
        self._id = Project.objects.count() + 1
        # insert the project to the projects table
        Project.objects.create(name=name, description=description, lead=lead)

    def __str__(self):
        return self.name

    def add_worker(self, worker):
        self.members.add(worker)
        self.save()

    def remove_worker(self, worker):
        self.members.remove(worker)
        self.save()

    def get_members(self):
        return self.members.all()

    def get_active_tasks(self):
        return self.tasks.filter(is_active=True)

    def delete_project(self):
        self.delete()

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

    def __init__(self, title, description, due_date, author, assignee=None, parent_task=None):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.author = author
        self.assignee = assignee
        self.parent_task = parent_task
        # create a uniqe id for the task base on the tasks sql db table
        self._id = Task.objects.count() + 1
        # insert the task to the tasks table
        Task.objects.create(title=title, description=description, due_date=due_date, author=author, assignee=assignee,
                            parent_task=parent_task)
    def __str__(self):
        return self.title
