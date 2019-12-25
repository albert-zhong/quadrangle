from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render

from .forms import ThreadForm, CommentForm
from .models import College, Thread, Comment


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
        thread = Thread.objects.get(slug=self.kwargs['thread_slug'])
        context['thread'] = thread
        context['comments'] = thread.comments.all()
        return context


class CommentCreateView(UserBelongsToCollegeMixin, FormView):
    def get_thread(self):
        return Thread.objects.get(slug=self.kwargs['thread_slug'])

    def get_success_url(self):
        return self.get_thread().get_absolute_url()

    # FormView fields and functions
    template_name = 'forum/new_comment.html'
    form_class = CommentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        new_comment = Comment(
            author=self.request.user,
            body=form.cleaned_data['body'],
            parent_thread=self.get_thread(),
        )
        # timestamp, score, and slug are automatically generated in models.py
        new_comment.save()
        return super().form_valid(form)


class CommentReplyCreateView(CommentCreateView):
    def get_parent_comment(self):
        return Comment.objects.get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        new_comment = Comment(
            author=self.request.user,
            body=form.cleaned_data['body'],
            parent_thread=self.get_thread(),
            parent=self.get_parent_comment(),
        )
        new_comment.save()
        return super().form_valid(form)
