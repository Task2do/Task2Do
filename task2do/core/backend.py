from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Manager, Worker

class ManagerBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            manager = Manager.objects.get(user_name=username)
            if manager.check_password(password):
                return manager
        except Manager.DoesNotExist:
            pass


class WorkerBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            worker = Worker.objects.get(user_name=username)
            if worker.check_password(password):
                return worker
        except Worker.DoesNotExist:
            pass
