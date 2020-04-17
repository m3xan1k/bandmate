from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.views import View
from django.http.request import HttpRequest
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin

from users.forms import SignUpForm, LogInForm


class SingUpView(View):

    name = 'signup'

    def get(self, request: HttpRequest) -> TemplateResponse:
        form = SignUpForm()
        return render(request, 'users/signup.html', {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SignUpForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            new_user = User(
                username=form_data['username'],
                email=form_data['email'],
            )
            new_user.set_password(form_data['password'])
            new_user.save()
            return redirect('login')
        return render(request, 'users/signup.html', {'form': form})


class LogInView(View):

    name = 'login'

    def get(self, request: HttpRequest) -> TemplateResponse:
        form = LogInForm()
        return render(request, 'users/login.html', {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = LogInForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            username = form_data['username']
            password = form_data['password']
            user: User = authenticate(request, username=username,
                                      password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)

        return redirect('dashboard_view')


class LogOutView(View):

    name = 'logout'

    def get(self, request: HttpRequest) -> HttpResponseRedirect:
        logout(request)
        return redirect('login')


class DashboardView(LoginRequiredMixin, View):

    name = 'dashboard_view'
    login_url = '/users/login/'

    def get(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse(b'<h1>Dashboard</h1>')
