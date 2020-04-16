from django.shortcuts import render, HttpResponse, redirect
from django.views import View
from django.http.request import HttpRequest
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from users.forms import SignUpForm


class SingUpView(View):

    name = 'signup_view'

    def get(self, request: HttpRequest) -> TemplateResponse:
        form = SignUpForm()
        return render(request, 'users/signup.html', {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SignUpForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            User.objects.create_user(
                username=form_data['username'],
                password=form_data['password'],
            )
            return redirect('dashboard_view')
        return render(request, 'users/signup.html', {'form': form})


class SignInView(View):

    name = 'signin_view'

    def get(self, request: HttpRequest) -> TemplateResponse:
        form = SignUpForm()
        return render(request, 'users/signin.html', {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SignUpForm(request.POST)
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


class DashboardView(View):

    name = 'dashboard_view'

    def get(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse(b'<h1>Dashboard</h1>')
