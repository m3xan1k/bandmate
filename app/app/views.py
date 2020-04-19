from django.shortcuts import render
from django.http import HttpRequest
from django.template.response import TemplateResponse


def home(request: HttpRequest) -> TemplateResponse:
    return render(request, 'home.html')
