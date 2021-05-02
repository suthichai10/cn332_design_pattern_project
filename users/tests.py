from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Max
# Create your tests here.

class UserLoginTest(TestCase):

    def setUp(self):
        # Create user
        User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1',
        )

    def test_login_page(self):
        """Check that user can access login page"""

        response = self.client.get('/login/')
        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        # Make sure that user access to the right page
        self.assertTemplateUsed(response, 'users/index.html')
    

    def test_login_valid_user(self):
        """Check that user can login with valid account"""

        # Login
        response = self.client.post('/login/', {
            'username': 'user1',
            'password': 'user1'}, 
            follow=True)

        # Check our correct user is logged in
        self.assertTrue(response.context['user'].is_active)
        self.assertEqual(str(response.context['user']), 'user1')
        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)

    def test_login_invalid_user(self):
        """Check that user can not login with invalid credentials"""

        # Login with invalid account
        response = self.client.post('/login/', {
            'username': 'notuser',
            'password': 'notuser'}, 
            follow=True)

        # Make sure that no user logged in
        self.assertFalse(response.context['user'].is_active)
        # Make sure that user still in login page
        self.assertTemplateUsed(response, 'users/index.html')
        # Check that invalid credential message is present
        self.assertEqual(response.context['message'], 'Invalid Credential')
        
        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        # Login
        self.client.login(username='user1', password='user1')
        response = self.client.post('/logout/')

        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        # Make sure that user still in login page
        self.assertTemplateUsed(response, 'pdf/upload.html')
        # Check that invalid credential message is present
        self.assertEqual(response.context['message'], 'Logged out')


class UserRegistrationTest(TestCase):
    def setUp(self):
        # Create user
        User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1',
        )

    def test_register_new_user(self):
        """Check that user can register new account"""

        response = self.client.post('/register/', {
            'username': 'user2',
            'email': 'user2@example.com',
            'password': 'user2',
            'repeated_password': 'user2'}, 
            follow=True)
        
        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        # Make sure that user is redirect to login page
        self.assertTemplateUsed(response, 'users/index.html')
        # Make sure that there is new user added into database with correct fields 
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(str(User.objects.get(username='user2')), 'user2')

    def test_register_existing_user(self):
        """Check that user can not register with username that already exist"""

        response = self.client.post('/register/', {
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'user1',
            'repeated_password': 'user1'}, 
            follow=True)

        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        # Make sure that user is still in register page
        self.assertTemplateUsed(response, 'users/register.html')
        # Make sure that there no new user added into database
        self.assertEqual(User.objects.count(), 1)
        # Make sure that message 'username has been used' is present
        self.assertEqual(response.context['message'], 'username has been used')

    def test_register_invalid_password_confirmation_user(self):
        """Check that user can not register with incorrect comfirm password"""

        response = self.client.post('/register/', {
            'username': 'user2',
            'email': 'user2@example.com',
            'password': 'user2',
            'repeated_password': 'wrongpassword'}, 
            follow=True)

        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        # Make sure that user is still in register page
        self.assertTemplateUsed(response, 'users/register.html')
        # Make sure that there no new user added into database
        self.assertEqual(User.objects.count(), 1)
        # Make sure that message 'Password did not match' is present
        self.assertEqual(response.context['message'], 'Password did not match')
