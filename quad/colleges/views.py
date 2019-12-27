from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect, get_object_or_404

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


@login_required
def view_forum(request, college_slug):
    college = get_object_or_404(College, slug=college_slug)
    user = request.user

    if not user.college == college and not user.is_staff:
        messages.warning(
            request,
            'You do not belong to this college.',
            extra_tags='alert-warning'
        )
        return redirect('home')

    template_name = 'forum/forum.html'
    threads = college.threads.all()
    context = {
        'college': college,
        'threads': threads,
    }

    return render(request, template_name, context)


@login_required
def create_thread(request, college_slug):
    college = get_object_or_404(College, slug=college_slug)
    user = request.user

    if not user.college == college and not user.is_staff:
        messages.warning(
            request,
            'You do not belong to this college.',
            extra_tags='alert-warning'
        )
        return redirect('home')

    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            new_thread = Thread(
                author=user,
                title=form.cleaned_data['title'],
                body=form.cleaned_data['body'],
                college=college,
            )
        new_thread.save()
        success_url = new_thread.get_absolute_url()
        return redirect(success_url)
    else:
        form = ThreadForm()

    template_name = 'forum/new_thread.html'
    context = {'form': form}

    return render(request, template_name, context)


@login_required
def view_thread(request, thread_slug):
    thread = get_object_or_404(
        Thread.objects.select_related('college'),
        slug=thread_slug
    )
    college = thread.college
    user = request.user

    if not user.college == college and not user.is_staff:
        messages.warning(
            request,
            'You do not belong to this college.',
            extra_tags='alert-warning'
        )
        return redirect('home')

    comments = thread.comments.all()

    template_name = 'forum/thread.html'
    context = {
        'college': college,
        'thread': thread,
        'comments': comments,
        'initial_like_status': get_like_status(user, thread, ThreadVote),
    }

    return render(request, template_name, context)


# helper function to see if the user has like/disliked the thread/comment.
# Vote object doesn't exist --> user hasn't voted --> like_status = 0
# Vote object exists, is_upvote=True --> user has liked --> like_status = 1
# Vote object exists, is_upvote=False --> user has disliked --> like_status = -1
def get_like_status(user, thread, vote_class):
    like_status = 0
    try:
        vote = vote_class.objects.get(
            voter=user,
            thread=thread
        )
        like_status = 1 if vote.is_upvote else -1
    except:
        pass

    return like_status


@login_required
def create_comment(request, thread_slug):
    thread = get_object_or_404(
        Thread.objects.select_related('college',),
        slug=thread_slug
    )
    college = thread.college
    user = request.user

    if not user.college == college and not user.is_staff:
        messages.warning(
            request,
            'You do not belong to this college.',
            extra_tags='alert-warning'
        )
        return redirect('home')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = Comment(
                author=user,
                body=form.cleaned_data['body'],
                parent_thread=thread,
            )
            # timestamp, score, and slug are automatically generated in models.py
            new_comment.save()
            success_url = thread.get_absolute_url()
            return redirect(success_url)
        else:
            msg = """ Sorry, something went with trying to make a comment!
                Please try again in a few minutes """
            messages.error(request, msg, extra_tags='alert-warning')
    else:
        form = CommentForm()

    template_name = 'forum/new_comment.html'
    context = {'form': form}

    return render(request, template_name, context)


@login_required
def reply_comment(request, comment_pk):
    parent_comment = get_object_or_404(
        Comment.objects.select_related('parent_thread__college'),
        pk=comment_pk
    )
    thread = parent_comment.parent_thread
    college = thread.college
    user = request.user

    if not user.college == college and not user.is_staff:
        messages.warning(
            request,
            'You do not belong to this college.',
            extra_tags='alert-warning'
        )
        return redirect('home')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = Comment(
                author=user,
                body=form.cleaned_data['body'],
                parent_thread=thread,
                parent=parent_comment
            )
            new_comment.save()
            success_url = thread.get_absolute_url()
            return redirect(success_url)
        else:
            msg = """ Sorry, something went with trying to make a comment!
                Please try again in a few minutes. """
            messages.error(request, msg, extra_tags='alert-warning')
    else:
        form = CommentForm()

    template_name = 'forum/new_comment.html'
    context = {'form': form}

    return render(request, template_name, context)


@login_required
def like_thread(request, thread_slug):
    thread = get_object_or_404(
        Thread.objects.select_related('college'),
        slug=thread_slug
    )
    college = thread.college
    user = request.user

    if not user.college == college and not user.is_staff:
        messages.warning(
            request,
            'You do not belong to this college.',
            extra_tags='alert-warning'
        )
        return redirect('home')

    if request.method == 'POST':
        user = request.user
        # if pressed == True, the like button was pressed.
        # if pressed = False, the dislike button was pressed.
        pressed = json.loads(request.POST['pressed'])
        if not isinstance(pressed, bool):
            msg = """ Sorry, something went with trying to like the post!
                Please try again in a few minutes. """
            messages.error(request, msg, extra_tags='alert-warning')

        result = {
            'success': True,
            'likeStatus': handle_thread_like(user, thread, pressed),
            'votes': thread.score
        }

    return HttpResponse(json.dumps(result), content_type='application/json')


def handle_thread_like(voter, thread, pressed):
    # Takes a voter (User object), thread, and a pressed (boolean value for
    # if like or dislike was pressed). Returns the resultant like_status state:
    # -1 means disliked, 0 means neutral, and +1 means liked. THIS IS NOT A 
    # PURE FUNCTION--it will appropiately update thread.score and either add,
    # delete, or modify a vote object.
    
    try:
        curr_vote = ThreadVote.objects.get(voter=voter, thread=thread)
        if curr_vote.is_upvote:
            if pressed:  # case: hit like once, hit like again to toggle
                like_status = 0
                thread.score -= 1
                curr_vote.delete()
            else:  # case: hit like once, hit dislike
                like_status = -1
                curr_vote.is_upvote = False
                curr_vote.save()
                thread.score -= 2
        else:
            if pressed:  # case: hit dislike once, hit like
                like_status = 1
                curr_vote.is_upvote = True
                curr_vote.save()
                thread.score += 2
            else:  # case: hit dislike once, hit dislike again to toggle
                like_status= 0
                thread.score += 1
                curr_vote.delete()
    except ThreadVote.DoesNotExist:
        new_vote = ThreadVote(
            voter=voter,
            is_upvote=pressed,
            thread=thread
        )
        new_vote.save()
        if pressed:  # case: hit like once
            like_status = 1
            thread.score += 1
        else:  # case: hit dislike once
            like_status = -1
            thread.score -= 1

    thread.save()
    return like_status
