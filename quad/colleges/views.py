from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render

from .forms import ThreadForm
from .models import College, Thread


class CollegeMixin:
    def get_college(self):
        return College.objects.get(slug=self.kwargs['slug'])


def get_college(slug):
    return College.objects.get(slug=slug)


# Displays all the threads for a college
class ForumView(CollegeMixin, TemplateView):
    template_name = 'forum/college_forum.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['college'] = self.get_college()
        return context


class ThreadCreateView(CollegeMixin, LoginRequiredMixin, UserPassesTestMixin, FormView):
    # LoginRequiredMixin fields and methods
    login_url = 'login'

    def get_success_url(self):
        return self.get_college().get_absolute_url()

    # UserPassesTestMixin function
    def test_func(self):
        user = self.request.user
        return user.is_staff or user.college == self.get_college()

    # FormView fields and functions
    template_name = 'forum/new_thread.html'
    form_class = ThreadForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        new_thread = Thread(
            author=self.request.user,
            title=form.cleaned_data['title'],
            body=form.cleaned_data['body'],
            college=self.get_college(),
        )
        # timestamp, score, and slug are automatically generated in models.py
        new_thread.save()
        return super().form_valid(form)
