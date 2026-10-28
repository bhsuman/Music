from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='authuser', password='password123')
        self.client = Client()

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_signup_page_renders(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse('login'), {'username': 'authuser', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

    def test_login_wrong_password(self):
        response = self.client.post(reverse('login'), {'username': 'authuser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Incorrect password!')

    def test_login_nonexistent_user(self):
        response = self.client.post(reverse('login'), {'username': 'nonexistent', 'password': 'password123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This user does not exist!')

    def test_signup_success(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
