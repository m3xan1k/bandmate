from django.shortcuts import render, HttpResponse, redirect
from django.views import View
from django.http.request import HttpRequest
from django.template.response import TemplateResponse
from django.contrib.auth.models import User

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
            return redirect('/')
        return render(request, 'users/signup.html', {'form': form})


class SignInView(View):

    name = 'singin_view'
