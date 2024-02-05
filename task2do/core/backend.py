from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Manager, Worker

class ManagerBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            manager = Manager.objects.get(personal_data__user__username=username)
            if manager.personal_data.user.password == password:
                return manager
        except Manager.DoesNotExist:
            pass


class WorkerBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            worker = Worker.objects.get(personal_data__user__username=username)
            if worker.personal_data.user.password == password:
                return worker
        except Worker.DoesNotExist:
            pass

def check_password(orig_password, try_password):
    return orig_password == try_password