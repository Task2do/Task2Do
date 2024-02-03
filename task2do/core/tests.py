from django.test import TestCase
from django.urls import reverse
from .models import Worker, Manager  # Adjust the import according to your app structure
from .forms import UserRegistrationForm
from django.core.exceptions import ImproperlyConfigured



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
