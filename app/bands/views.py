from typing import Union, Optional

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponseRedirect, QueryDict
from django.template.response import TemplateResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.db.models.query import QuerySet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from bands.forms import MusicianProfileForm, MusicianFilterForm
from bands.models import Musician, Instrument


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
                # exception for instruments m2m field
                except TypeError:
                    musician.instruments.set(form_data[field])
            musician.save()
            messages.success(request, 'Profile saved')
            return redirect(UserDashboardView.name)
        return render(request, 'bands/profile_edit.html', {'form': form})


class MusiciansView(View):

    name = 'musicians'
    form = MusicianFilterForm

    def get(self, request: HttpRequest, id: Union[str, int] = None) -> TemplateResponse:
        form = self.form(request.GET)
        if not id:
            musicians = Musician.activated_objects.all()
            '''Check for filter params'''
            if request.GET:
                musicians = self.apply_filters(musicians, request.GET)
            '''Apply order'''
            musicians = musicians.order_by('is_busy')

            '''Show 9 musicians per page'''
            paginator = Paginator(musicians, 9)
            page = request.GET.get('page')
            try:
                musicians = paginator.page(page)
            except PageNotAnInteger:
                musicians = paginator.page(1)
            except EmptyPage:
                musicians = paginator.page(paginator.num_pages)

            context = {
                'musicians': musicians,
                'form': form,
            }
            return render(request, 'bands/musicians.html', context)
        musician = get_object_or_404(Musician, id=id)
        return render(request, 'bands/musician.html', {'musician': musician})

    def apply_filters(self, musicians: QuerySet, filters: QueryDict) -> Optional[QuerySet]:
        '''Extract all filters'''
        city_id = filters.get('city')
        instrument_id = filters.get('instrument')

        '''Apply filters'''
        if city_id:
            musicians = musicians.filter(city_id=city_id).all()
        if instrument_id:
            instrument = Instrument.objects.filter(id=instrument_id).first()
            musicians = musicians.filter(instruments__in=[instrument]).all()

        return musicians
