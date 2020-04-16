from django.test import TestCase
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.contrib.auth import get_user_model
from django.urls import reverse

from users.views import SingUpView, SignInView


class TestUsers(TestCase):

    SIGNUP_URL = reverse(SingUpView.name)
    SIGNIN_URL = reverse(SignInView.name)

    def setUp(self):
        self.request = HttpRequest()

    def test_get_sign_up(self):
        response = self.client.get(self.SIGNUP_URL)
        assert response.status_code == 200

    def test_sign_up(self):
        self.request.POST['username'] = 'test_user'
        self.request.POST['password'] = 'test_password'
        response: HttpResponse = SingUpView().post(self.request)
        assert response.status_code == 302

        User = get_user_model()
        new_user: User = User.objects.first()
        assert new_user.username == 'test_user'
        assert new_user.is_staff is False
        assert new_user.is_active is True

    def test_sign_up_empty_password(self):
        self.request.POST['username'] = 'test_user'
        response: HttpResponse = SingUpView().post(self.request)
        assert response.status_code == 200
        User = get_user_model()
        assert User.objects.count() == 0

    def test_sign_up_empty_username(self):
        self.request.POST['password'] = 'test_password'
        response: HttpResponse = SingUpView().post(self.request)
        assert response.status_code == 200
        User = get_user_model()
        assert User.objects.count() == 0

    def test_get_sign_in(self):
        response = self.client.get(self.SIGNIN_URL)
        assert response.status_code == 200
