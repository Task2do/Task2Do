from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

from .models import Worker, Manager, PersonalData, Task, Project
from .forms import UserRegistrationForm
import datetime

class WorkerTests(TestCase):
    def setUp(self):
        self.worker = Worker.objects.create(user_name='testworker', password='pwd123', first_name='Test', last_name='Worker', email='testworker@example.com')

    def test_update_password(self):
        self.worker.update_password('newpassword')
        self.assertEqual(self.worker.password, 'newpassword')

    def test_update_email(self):
        self.worker.update_email('newemail@example.com')
        self.assertEqual(self.worker.email, 'newemail@example.com')

    def test_update_b_date(self):
        new_b_date = datetime.date(2000, 1, 1)
        self.worker.update_b_date(new_b_date)
        self.assertEqual(self.worker.b_date, new_b_date)

    def test_get_full_name(self):
        self.assertEqual(self.worker.get_full_name(), 'Test Worker')

    def test_is_birthday_today(self):
        self.worker.b_date = datetime.date.today()
        self.assertTrue(self.worker.is_birthday_today())

    def test_delete_user(self):
        self.worker.delete_user()
        self.assertFalse(Worker.objects.filter(user_name='testworker').exists())

class ManagerTests(TestCase):
    def setUp(self):
        self.manager = Manager.objects.create(user_name='testmanager', password='pwd123', first_name='Test', last_name='Manager', email='testmanager@example.com')

    def test_update_password(self):
        self.manager.update_password('newpassword')
        self.assertEqual(self.manager.password, 'newpassword')

    def test_update_email(self):
        self.manager.update_email('newemail@example.com')
        self.assertEqual(self.manager.email, 'newemail@example.com')

    def test_update_b_date(self):
        new_b_date = datetime.date(2000, 1, 1)
        self.manager.update_b_date(new_b_date)
        self.assertEqual(self.manager.b_date, new_b_date)

    def test_get_full_name(self):
        self.assertEqual(self.manager.get_full_name(), 'Test Manager')

    def test_is_birthday_today(self):
        self.manager.b_date = datetime.date.today()
        self.assertTrue(self.manager.is_birthday_today())

    def test_delete_user(self):
        self.manager.delete_user()
        self.assertFalse(Manager.objects.filter(user_name='testmanager').exists())
class UserCreationTests(TestCase):
    def setUp(self):
        # Setup data or prerequisites for the tests
        self.user_data = {
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'testpassword123',  # Assuming your form has a password confirmation field
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'user_type': 'worker',  # or 'manager'
            'birth_date': '2000-01-01',
        }

    def test_create_worker(self):
        # Simulate form submission for worker creation
        self.user_data['user_type'] = 'worker'
        response = self.client.post(reverse('signup'), self.user_data)
        self.assertEqual(response.status_code, 302)  # Assuming redirect to 'signup_success'
        self.assertTrue(Worker.objects.filter(email='testuser@example.com').exists())

    def test_create_manager(self):
        # Simulate form submission for manager creation
        self.user_data['user_type'] = 'manager'
        response = self.client.post(reverse('signup'), self.user_data)
        self.assertEqual(response.status_code, 302)  # Assuming redirect to 'signup_success'
        self.assertTrue(Manager.objects.filter(email='testuser@example.com').exists())

    def test_duplicate_email_error(self):
        # Create a Worker with an email
        Worker.objects.create(user_name='existinguser', password='pwd123', first_name='Existing', last_name='User', email='existing@example.com')
        # Attempt to create another Worker with the same email
        self.user_data['email'] = 'existing@example.com'
        response = self.client.post(reverse('signup'), self.user_data)
        self.assertEqual(response.status_code, 200)  # Assuming it returns to the form with an error
        self.assertFormError(response, 'form', 'email', 'Email already exists for this user type. Please choose another one.')

    # You can add more tests to cover other cases like form validation, incorrect data submissions, etc.
