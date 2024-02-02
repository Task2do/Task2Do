from django.db import models

#global variables
#the type of the request
REQUEST_TYPE = {
    'JOIN': 'join', # when joining a project
    'LEAVE': 'leave', # when leaving a project
    'CREATE': 'create', # when creating a task
    'UPDATE': 'update', # when updating a task
    'FINISH': 'finish', # when finishing a task
}
#the status of the task
STATUS_CHOICES = {
    'NOT STARTED': 'Not Started',
    'IN PROGRESS': 'In Progress',
    'ADVANCED': 'Advanced', # when the task is advanced
    'ON HOLD': 'On Hold', # when the task is on hold
    'CANCELED': 'Canceled', # when the task is canceled
    'BLOCKED': 'Blocked', # when the task is blocked
    'COMPLETED': 'Completed',
}


class PersonalData(models.Model):
    '''
    PersonalData model representing personal data of a user.
    '''
    user_name = models.CharField(max_length=75, primary_key=True) # this the PK of the model
    password = models.CharField(max_length=75) #must have
    first_name = models.CharField(max_length=30) #must have
    last_name = models.CharField(max_length=75) #must have
    email = models.EmailField() #must have
    b_date = models.DateField() # not must have

    def __init__(self, usr_name, pwd, f_name, l_name, email, b_date=None):
        self.user_name = usr_name
        self.password = pwd
        self.first_name = f_name
        self.last_name = l_name
        self.email = email
        self.b_date = b_date
class Worker(PersonalData):
    _id = models.AutoField(primary_key=True)

    def __init__(self, usr_name, pwd, f_name, l_name, email, b_date=None):
        super().__init__(usr_name, pwd, f_name, l_name, email, b_date)
        #create a uniqe id for the worker base on the workers sql db table
        self._id = Worker.objects.count() + 1
        #insert the worker to the workers table
        Worker.objects.create(user_name=usr_name, password=pwd, first_name=f_name, last_name=l_name, email=email, b_date=b_date)


class Manager(PersonalData):
    _id = models.AutoField(primary_key=True)

    def __init__(self, usr_name, pwd, f_name, l_name, email, b_date=None):
        super.__init__(usr_name, pwd, f_name, l_name, email, b_date)
        #create a uniqe id for the manager base on the managers sql db table
        self._id = Manager.objects.count() + 1
        #insert the manager to the managers table
        Manager.objects.create(user_name=usr_name, password=pwd, first_name=f_name, last_name=l_name, email=email, b_date=b_date)

class Request(models.Model):
    '''
    Request model representing a request from a user to join a project.
    '''
    request_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=10, choices=REQUEST_TYPE)
    # using the usr _id
    last_sender = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='sent_requests')
    last_receiver = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='reveiver') #using the usr _id
    content = models.TextField(max_length=2048)
    header = models.CharField(max_length=128)

    def __init__(self, type, last_sender, last_receiver, content, header):
        self.type = type
        self.last_sender = last_sender
        self.last_receiver = last_receiver
        self.content = content
        self.header = header
        #insert the request to the requests table
        Request.objects.create(type=type, last_sender=last_sender, last_receiver=last_receiver, content=content, header=header)

class Project(models.Model):
    """
       Project model representing a team project with a name, a lead, and members.
       """
    _id = models.AutoField(primary_key=True)
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
    _id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Not Started')
    author = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='authored_tasks')
    assignee = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_tasks')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
