from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class HomePageTest(TestCase):

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


class LoginTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

    def test_login(self):
        login = self.client.login(
            username='testuser',
            password='testpassword123'
        )

        self.assertTrue(login)


class RegisterPageTest(TestCase):

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
