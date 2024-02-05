from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Manager, Worker
from django.contrib.auth.hashers import check_password


class ManagerBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            manager = Manager.objects.get(personal_data__user__username=username)
            user = manager.personal_data.user
            # Use Django default password checker
            if user.check_password(password):
                return user
        except Manager.DoesNotExist:
            pass


class WorkerBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            worker = Worker.objects.get(personal_data__user__username=username)
            user = worker.personal_data.user
            # Use Django default password checker
            if user.check_password(password):
                return user
        except Worker.DoesNotExist:
            pass


def check_password(orig_password, try_password):
    return orig_password == try_password