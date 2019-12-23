from django.shortcuts import render
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = 'layout/home.html'


class AboutPageView(TemplateView):
    template_name = 'layout/about.html'
