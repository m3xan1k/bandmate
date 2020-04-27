from typing import Union, Optional
from datetime import timedelta

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpRequest, HttpResponseRedirect, QueryDict
from django.template.response import TemplateResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.db.models import QuerySet
from django.utils import timezone

from board.models import Announcement
from board.forms import AnnouncementEditForm, AnnouncementFilterForm
from helpers.authority import check_user


class AnnouncementDashboardView(LoginRequiredMixin, View):

    name = 'announcements_dashboard'
    login_url = '/users/login/'

    def get(self, request: HttpRequest) -> Union[TemplateResponse, HttpResponseRedirect]:
        announcements = Announcement.objects.filter(author=request.user).all()
        return render(request, 'board/announcements_dashboard.html',
                      {'announcements': announcements})


class AnnouncementEditView(LoginRequiredMixin, View):

    name = 'announcement_edit'
    login_url = '/users/login/'
    form = AnnouncementEditForm

    @check_user(model=Announcement, attribute='author')
    def get(self, request: HttpRequest,
            id: Optional[str] = None) -> Union[TemplateResponse, HttpResponseRedirect]:
        if id is not None:
            announcement = get_object_or_404(Announcement, id=id)
            form = self.form(instance=announcement)
            return render(request, 'board/announcement_edit.html', {'form': form})
        return render(request, 'board/announcement_edit.html', {'form': self.form()})

    def post(self, request: HttpRequest) -> Union[TemplateResponse, HttpResponseRedirect]:
        form = self.form(request.POST)
        if form.is_valid():
            new_announcement = form.save(commit=False)
            new_announcement.author = request.user
            new_announcement.save()
            messages.success(request, 'New announcement created')
            return redirect(reverse(AnnouncementDashboardView.name))
        return render(request, 'board/announcement_edit.html', {'form': form})

    @check_user(model=Announcement, attribute='author')
    def put(self, request: HttpRequest,
            id: str) -> Union[HttpResponseRedirect, TemplateResponse]:
        announcement = get_object_or_404(Announcement, id=id)
        '''Check if announcement update request wanted'''
        if request.GET.get('update'):
            update_interval = timezone.now() - timedelta(hours=4)
            if announcement.updated_at > update_interval:
                messages.warning(request, 'Announcement may be updated once every 4 hours')
                return redirect(AnnouncementDashboardView.name)
            announcement.updated_at = timezone.now()
            announcement.save()
            messages.info(request, 'Announcement updated')
            return redirect(AnnouncementDashboardView.name)
        form = self.form(request.PUT, instance=announcement)
        if form.is_valid():
            form.save()
            messages.info(request, 'Announcement saved')
            return redirect(AnnouncementDashboardView.name)
        return render(request, 'board/announcement_edit.html', {'form': form})

    @check_user(model=Announcement, attribute='author')
    def delete(self, request: HttpRequest, id: str) -> HttpResponseRedirect:
        announcement = get_object_or_404(Announcement, id=id)
        announcement.delete()
        messages.info(request, 'Announcement deleted')
        return redirect(AnnouncementDashboardView.name)


class AnnouncementsView(View):

    name = 'announcements'
    form = AnnouncementFilterForm

    def get(self, request: HttpRequest, id: str = None) -> TemplateResponse:
        if id is not None:
            announcement = get_object_or_404(Announcement, id=id)
            return render(request, 'board/announcement.html', {'announcement': announcement})
        form = self.form(request.GET)
        announcements = Announcement.active.all()
        if request.GET:
            announcements = self.apply_filters(announcements, request.GET)
        context = {
            'form': form,
            'announcements': announcements,
        }
        return render(request, 'board/announcements.html', context)

    def apply_filters(self, announcements: QuerySet, filters: QueryDict) -> QuerySet:
        category = filters.get('category')

        if category:
            announcements = announcements.filter(category=category).all()

        return announcements
