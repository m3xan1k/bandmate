from django.test import TestCase
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.urls import reverse

from users.views import SingUpView, SignInView, DashboardView


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
            'username': 'test_user',
            'password': 'test_password',
        }
        response: HttpResponse = self.client.post(self.SIGNUP_URL,
                                                  request_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(DashboardView.name))

        User = get_user_model()
        new_user: User = User.objects.first()
        self.assertEqual(new_user.username, 'test_user')
        self.assertFalse(new_user.is_staff)
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


class TestSignIn(TestCase):

    SIGNIN_URL = reverse(SignInView.name)

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
        response = self.client.get(self.SIGNIN_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('users/signin.html')

    def test_post_sign_in(self):
        response = self.client.post(
            path=self.SIGNIN_URL,
            data={
                'username': 'test_user',
                'password': 'test_password',
            }
        )
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse(DashboardView.name))
