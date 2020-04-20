from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages

from bands.forms import MusicianProfileForm
from bands.models import Musician


def home(request: HttpRequest) -> TemplateResponse:
    return render(request, 'home.html')


class UserDashboardView(LoginRequiredMixin, View):

    name = 'user_dashboard'
    login_url = '/users/login/'

    def get(self, request: HttpRequest) -> TemplateResponse:
        return render(request, 'bands/user_dashboard.html')


class ProfileEditView(LoginRequiredMixin, View):

    name = 'profile_edit'
    login_url = '/users/login/'
    form = MusicianProfileForm

    def get(self, request: HttpRequest) -> TemplateResponse:
        musician = Musician.objects.filter(user=request.user).first()
        form = self.form(instance=musician)
        return render(request, 'bands/profile_edit.html', {'form': form})

    def post(self, request: HttpRequest) -> HttpResponseRedirect:
        form = self.form(request.POST)
        musician = Musician.objects.filter(user=request.user).first()
        if form.is_valid():
            form_data = form.cleaned_data
            for field in form_data:
                try:
                    setattr(musician, field, form_data[field])
                # exception for instruments
                except TypeError:
                    musician.instruments.set(form_data[field])
            musician.save()
            messages.success(request, 'Profile saved')
            return redirect(UserDashboardView.name)
        return render(request, 'bands/profile_edit.html', {'form': form})
