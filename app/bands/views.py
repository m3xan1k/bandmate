from django.shortcuts import render
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View


class UserDashboardView(LoginRequiredMixin, View):

    name = 'dashbord'
    login_url = '/users/login/'

    def get(self, request: HttpRequest) -> TemplateResponse:
        return render(request, 'bands/user_dashboard.html')


class ProfileView(LoginRequiredMixin, View):

    name = 'profile'
    login_url = '/users/login/'

    def get(self, request: HttpRequest) -> TemplateResponse:
        pass
