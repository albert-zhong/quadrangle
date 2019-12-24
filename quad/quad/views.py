from django.shortcuts import render
from django.views.generic import TemplateView

from colleges.models import College


class HomePageView(TemplateView):
    template_name = 'layout/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['colleges'] = College.objects.all()
        return context


class AboutPageView(TemplateView):
    template_name = 'layout/about.html'
