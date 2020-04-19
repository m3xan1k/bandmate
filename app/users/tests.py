from django.test import TestCase
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.urls import reverse

from users.views import (
    SingUpView, LogInView, DashboardView, LogOutView,
    PasswordChangeView,
)


class TestSignUp(TestCase):

    SIGNUP_URL = reverse(SingUpView.name)

    def setUp(self):
        self.request = HttpRequest()

    def test_get_sign_up(self):
        response = self.client.get(self.SIGNUP_URL)
        assert response.status_code == 200
        self.assertTemplateUsed('users/signup.html')

    def test_sign_up(self):
        request_data = {
            'email': 'test@email.com',
            'username': 'test_user',
            'password': 'test_password',
            'confirm_password': 'test_password',
        }
        response: HttpResponse = self.client.post(self.SIGNUP_URL,
                                                  request_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(LogInView.name))

        User = get_user_model()
        new_user: User = User.objects.first()
        self.assertEqual(new_user.username, 'test_user')
        self.assertFalse(new_user.is_staff)
        self.assertFalse(new_user.is_superuser)
        self.assertTrue(new_user.is_active)

    def test_sign_up_empty_password(self):
        self.request.POST['username'] = 'test_user'
        response: HttpResponse = SingUpView().post(self.request)
        User = get_user_model()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_sign_up_empty_username(self):
        self.request.POST['password'] = 'test_password'
        response: HttpResponse = SingUpView().post(self.request)
        User = get_user_model()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_sign_up_empty_email(self):
        request_data = {
            'username': 'test_user',
            'password': 'test_password',
            'confirm_password': 'test_password',
        }
        response: HttpResponse = self.client.post(self.SIGNUP_URL,
                                                  request_data)
        self.assertTemplateUsed(response, 'users/signup.html')

        User = get_user_model()
        self.assertEqual(User.objects.count(), 0)


class TestLogIn(TestCase):

    LOGIN_URL = reverse(LogInView.name)
    LOGOUT_URL = reverse(LogOutView.name)

    @classmethod
    def setUpClass(cls):
        User = get_user_model()
        User.objects.create_user(
            username='test_user',
            password='test_password',
        )

    @classmethod
    def tearDownClass(cls):
        User = get_user_model()
        User.objects.all().delete()

    def test_get_sign_in(self):
        response = self.client.get(self.LOGIN_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('users/login.html')

    def test_post_sign_in(self):
        response = self.client.post(
            path=self.LOGIN_URL,
            data={
                'username': 'test_user',
                'password': 'test_password',
            }
        )
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(DashboardView.name))

    def test_logout(self):
        self.client.post(
            path=self.LOGIN_URL,
            data={
                'username': 'test_user',
                'password': 'test_password',
            }
        )
        response = self.client.get(self.LOGOUT_URL)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)
        self.assertRedirects(response, reverse(LogInView.name))


class TestPasswordChange(TestCase):

    LOGIN_URL = reverse(LogInView.name)
    LOGOUT_URL = reverse(LogOutView.name)
    PASSWORD_CHANGE_URL = reverse(PasswordChangeView.name)
    DASHBOARD_URL = reverse(DashboardView.name)

    def setUp(self):
        User = get_user_model()
        User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        login_data = {
            'username': 'test_user',
            'password': 'test_password',
        }
        self.client.post(self.LOGIN_URL, login_data)

    def tearDown(self):
        self.client.get(self.LOGOUT_URL)
        User = get_user_model()
        User.objects.all().delete()

    def test_get_password_change(self):
        response: HttpResponse = self.client.get(self.PASSWORD_CHANGE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/password_change.html')

    def test_get_password_change_unauthorized(self):
        self.client.get(self.LOGOUT_URL)
        response: HttpResponse = self.client.get(self.PASSWORD_CHANGE_URL)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_anonymous)
        self.assertFalse(user.is_authenticated)
        self.assertRedirects(response,
                             f'{self.LOGIN_URL}?next={self.PASSWORD_CHANGE_URL}')

    def test_post_password_change(self):
        data = {
            'old_password': 'test_password',
            'password': 'new_password',
            'confirm_password': 'new_password',
        }
        response = self.client.post(self.PASSWORD_CHANGE_URL, data=data)
        self.assertRedirects(response, self.LOGIN_URL)

        User = get_user_model()
        user = User.objects.filter(username='test_user').first()
        self.assertTrue(user.check_password(data['password']))

    def test_post_password_change_wrong_old_password(self):
        data = {
            'old_password': 'wrong_password',
            'password': 'new_password',
            'confirm_password': 'new_password',
        }
        response = self.client.post(self.PASSWORD_CHANGE_URL, data=data)
        self.assertTemplateUsed(response, 'users/password_change.html')

        correct_password = 'test_password'
        user = auth.get_user(self.client)
        self.assertTrue(user.check_password(correct_password))


class TestDashboard(TestCase):

    DASHBOARD_URL = reverse(DashboardView.name)

    @classmethod
    def setUpClass(cls):
        User = get_user_model()
        User.objects.create_user(
            username='test_user',
            password='test_password',
        )

    @classmethod
    def tearDownClass(cls):
        User = get_user_model()
        User.objects.all().delete()

    def test_unauthorized_access(self):
        response: HttpResponse = self.client.get(self.DASHBOARD_URL)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse(LogInView.name) + f'?next={self.DASHBOARD_URL}',
        )

    def test_authorized_access(self):
        self.client.post(
            path=reverse(LogInView.name),
            data={
                'username': 'test_user',
                'password': 'test_password',
            }
        )
        response: HttpResponse = self.client.get(self.DASHBOARD_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('users/dashboard.html')
