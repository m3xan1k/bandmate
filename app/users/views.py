from typing import Union

from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.views import View
from django.http.request import HttpRequest
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from users.forms import SignUpForm, LogInForm, PasswordChangeForm
from bands.views import UserDashboardView


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
            messages.success(request, 'You successfully registered')
            return redirect(LogInView.name)
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
                    messages.success(request, 'You logged in')
                    return redirect(UserDashboardView.name)
                messages.error(request, 'Account disabled')
                return render(request, 'users/login.html', {'form': form})
            messages.error(request, 'Wrong password or username')
            return render(request, 'users/login.html', {'form': form})
        messages.error(request, 'Wrong password or username')
        return render(request, 'users/login.html', {'form': form})


class LogOutView(View):

    name = 'logout'

    def get(self, request: HttpRequest) -> HttpResponseRedirect:
        logout(request)
        messages.info(request, 'You logged out')
        return redirect(LogInView.name)


class PasswordChangeView(LoginRequiredMixin, View):

    name = 'password_change'
    login_url = '/users/login/'

    def get(self, request: HttpRequest) -> TemplateResponse:
        form = PasswordChangeForm()
        return render(request, 'users/password_change.html', {'form': form})

    def post(self, request: HttpRequest) -> Union[HttpResponseRedirect,
                                                  HttpResponse]:
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            user: User = User.objects.filter(username=request.user).first()
            if user.check_password(form_data['old_password']):
                user.set_password(form_data['password'])
                user.save()
                messages.info(request, 'Password changed')
                return redirect(LogInView.name)
            messages.error(request, 'Wrong password')
            return render(request, 'users/password_change.html', {'form': form})
        messages.error(request, 'Passwords not match')
        return render(request, 'users/password_change.html', {'form': form})
