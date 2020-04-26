from typing import Union, Optional

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages

from board.models import Announcement
from board.forms import AnnouncementEditForm
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
