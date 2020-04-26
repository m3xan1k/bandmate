from typing import Union

from django.shortcuts import render
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from board.models import Announcement


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

    def get(self, request: HttpRequest) -> Union[TemplateResponse, HttpResponseRedirect]:
        return render(request, 'board/announcement_edit.html')
