from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render

from .forms import ThreadForm
from .models import College, Thread


# Requires that the requested user belongs to the college
class UserBelongsToCollegeMixin(LoginRequiredMixin, UserPassesTestMixin):
    def get_college(self):
        return College.objects.get(slug=self.kwargs['college_slug'])

    # LoginRequiredMixin fields and methods
    login_url = 'login'

    def get_success_url(self):
        return self.get_college().get_absolute_url()

    # UserPassesTestMixin function
    def test_func(self):
        user = self.request.user
        return user.is_staff or user.college == self.get_college()


# Displays all the threads for a college
class ForumView(UserBelongsToCollegeMixin, TemplateView):
    template_name = 'forum/college_forum.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['college'] = self.get_college()
        return context


class ThreadCreateView(UserBelongsToCollegeMixin, FormView):
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


class ThreadListView(UserBelongsToCollegeMixin, TemplateView):
    template_name = 'forum/thread_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['thread'] = Thread.objects.get(slug=self.kwargs['thread_slug'])
        return context
