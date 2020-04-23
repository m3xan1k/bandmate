from typing import Union, Optional

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponseRedirect, QueryDict
from django.template.response import TemplateResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.db.models.query import QuerySet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied

from bands.forms import MusicianProfileForm, MusicianFilterForm, BandEditForm
from bands.models import Musician, Instrument, Band


class HomeView(View):

    name = 'home_view'

    def get(self, request: HttpRequest) -> TemplateResponse:
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

    def post(self, request: HttpRequest) -> Union[HttpResponseRedirect, TemplateResponse]:
        musician = Musician.objects.filter(user=request.user).first()
        form = self.form(request.POST, instance=musician)
        if form.is_valid():
            form.save()
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


class BandsDashboardView(LoginRequiredMixin, View):

    name = 'bands_dashboard'
    login_url = '/users/login/'

    def get(self, request: HttpRequest) -> TemplateResponse:
        bands = Band.objects.filter(admin=request.user).all()
        return render(request, 'bands/bands_dashboard.html', {'bands': bands})


class BandEditView(LoginRequiredMixin, View):

    name = 'band_edit'
    login_url = '/users/login/'
    form = BandEditForm

    def get(self, request: HttpRequest, id: Union[str, int] = None) -> TemplateResponse:
        '''If requested new band creation'''
        if id is None:
            form = self.form()
            return render(request, 'bands/band_edit.html', {'form': form})

        '''Check if band exists and correct user trying to edit band'''
        band = get_object_or_404(Band, id=id)
        if not band.admin == request.user:
            raise PermissionDenied
        form = self.form(instance=band)
        return render(request, 'bands/band_edit.html', {'form': form})

    def post(self, request: HttpRequest) -> Union[TemplateResponse, HttpResponseRedirect]:
        '''Creating new band'''
        form = self.form(request.POST)
        if form.is_valid():
            '''Assign simple fields'''
            band = form.save(commit=False)
            '''Define admin and save'''
            band.admin = request.user
            band.save()
            '''Save rest of fields'''
            form.save_m2m()
            messages.info(request, 'Band created')
            return redirect(BandsDashboardView.name)
        return render(request, 'bands/band_edit.html', {'form': form})

    def put(self, request: HttpRequest, id: Union[str, int]) -> HttpResponseRedirect:
        '''edit existed record'''
        print(request.POST)
        band = get_object_or_404(Band, id=id)
        if not band.admin == request.user:
            raise PermissionDenied
        form = self.form(request.POST, instance=band)
        if form.is_valid():
            band = form.save()
            messages.info(request, 'Band info updated')
            return redirect(BandsDashboardView.name)
        return render(request, 'bands/band_edit.html', {'form': form})

    def delete(self, request: HttpRequest, id: Union[str, int]) -> HttpResponseRedirect:
        band = get_object_or_404(Band, id=id)
        if not band.admin == request.user:
            raise PermissionDenied
        band.delete()
        messages.info(request, 'Band deleted')
        return redirect(BandsDashboardView.name)


class BandsView(View):

    name = 'bands'

    def get(self, request: HttpRequest, id: Union[int, str] = None) -> TemplateResponse:
        if id is None:
            bands = Band.objects.all()
            '''Check filters'''
            if request.GET:
                bands = self.apply_filters(bands, request.GET)

            return render(request, 'bands/bands.html', {'bands': bands})

        band = get_object_or_404(Band, id=id)
        return render(request, 'bands/bands.html', {'band': band})

    def apply_filters(self, bands: QuerySet, filters: QueryDict) -> QuerySet:
        city_id = filters.get('city')
        style_id = filters.get('style')

        if city_id:
            bands = bands.filter(city_id=city_id).all()

        if style_id:
            bands = bands.filter(styles__in=[style_id]).all()

        return bands
