from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render

import json
from .forms import ThreadForm, CommentForm
from .models import College, Thread, Comment, ThreadVote, CommentVote


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
        curr_thread = Thread.objects.get(slug=self.kwargs['thread_slug'])
        context['thread'] = curr_thread
        context['comments'] = curr_thread.comments.all()

        # -1 = disliked, 0 = hasn't voted, +1 = liked
        like_status = 0
        try:
            vote = ThreadVote.objects.get(
                voter=self.request.user,
                thread=curr_thread
            )
            like_status = 1 if vote.is_upvote else -1
        except:
            pass

        context['initial_like_status'] = like_status
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

# eventually put user verification here
def like_thread(request, thread_slug):
    if request.method == 'POST':
        user = request.user
        curr_thread = Thread.objects.get(slug=thread_slug)

        # if pressed == True, the like button was pressed.
        # if pressed = False, the dislike butto was pressed.
        pressed = json.loads(request.POST['pressed'])
        assert isinstance(pressed, bool)

        result = {'success': True}

        try:
            curr_vote = ThreadVote.objects.get(voter=user, thread=curr_thread)
            if curr_vote.is_upvote:
                if pressed:  # case: hit like once, hit like again to toggle
                    result['likeStatus'] = 0
                    curr_thread.score -= 1
                    curr_vote.delete()
                else:  # case: hit like once, hit dislike
                    result['likeStatus'] = -1
                    curr_vote.is_upvote = False
                    curr_vote.save()
                    curr_thread.score -= 2
            else:
                if pressed:  # case: hit dislike once, hit like
                    result['likeStatus'] = 1
                    curr_vote.is_upvote = True
                    curr_vote.save()
                    curr_thread.score += 2
                else:  # case: hit dislike once, hit dislike again to toggle
                    result['likeStatus'] = 0
                    curr_thread.score += 1
                    curr_vote.delete()
        except ThreadVote.DoesNotExist:
            new_vote = ThreadVote(
                voter=user,
                is_upvote=pressed,
                thread=curr_thread
            )
            new_vote.save()
            if pressed:  # case: hit like once
                result['likeStatus'] = 1
                curr_thread.score += 1
            else:  # case: hit dislike once
                result['likeStatus'] = -1
                curr_thread.score -= 1

        curr_thread.save()
        result['votes'] = curr_thread.score

    return HttpResponse(json.dumps(result), content_type='application/json')
