from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

import json
from .forms import ThreadForm, CommentForm
from .models import College, Thread, Comment, ThreadVote, CommentVote


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
            messages.success(
                request,
                'New thread successfully made!',
                extra_tags='alert-success'
            )
            return redirect(new_thread)
        else:
            messages.warning(
                request,
                'Sorry, something went wrong with making that thread!',
                extra_tags='alert-warning'
            )
            return redirect(college)

    template_name = 'forum/new_thread.html'
    form = ThreadForm()
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
def delete_thread(request, thread_slug):
    thread = get_object_or_404(
        Thread.objects.select_related('college', 'author'),
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

    author = thread.author
    if not user == author and not user.is_staff:
        messages.warning(
            request,
            'You can only delete your own threads!',
            extra_tags='alert-warning'
        )
        return redirect(thread)
        
    if request.method == 'POST':
        thread.delete()
        messages.success(
            request,
            'Your thread has successfully been deleted!',
            extra_tags='alert-success'
        )
        return redirect(college)

    template_name = 'forum/delete_thread.html'
    context = {
        'thread': thread,
        'college': college,
        'author': author,
    }
    return render(request, template_name, context)


@login_required
def edit_thread(request, thread_slug):
    thread = get_object_or_404(
        Thread.objects.select_related('college', 'author'),
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

    author = thread.author
    if not user == author and not user.is_staff:
        messages.warning(
            request,
            'You can only edit your own threads!',
            extra_tags='alert-warning'
        )
        return redirect(thread)
        
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread.title = form.cleaned_data['title']
            thread.body = form.cleaned_data['body']
            thread.save()
            messages.success(
                request,
                'Thread successfully updated!',
                extra_tags='alert-success'
            )
            return redirect(thread)
        else:
            messages.warning(
                request,
                'Sorry, something went wrong with editing that thread!',
                extra_tags='alert-warning'
            )

    template_name = 'forum/new_thread.html'

    initial_values = {
        'title': thread.title,
        'body': thread.body,
    }
    form = ThreadForm(initial=initial_values)
    context = {
        'form': form,
    }

    return render(request, template_name, context)


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

    template_name = 'forum/new_comment.html'
    form = CommentForm()
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

    template_name = 'forum/new_comment.html'
    form = CommentForm()
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
        # if pressed == True, the like button was pressed.
        # if pressed = False, the dislike button was pressed.
        pressed = json.loads(request.POST['pressed'])
        if not isinstance(pressed, bool):
            msg = """ Sorry, something went wrong with trying to like the post!
                Please try again in a few minutes. """
            messages.error(request, msg, extra_tags='alert-error')
        else:
            result = {
                'success': True,
                'likeStatus': handle_thread_like(user, thread, pressed),
                'votes': thread.score
            }
            return HttpResponse(
                json.dumps(result),
                content_type='application/json'
            )


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


@login_required
def like_comment(request, comment_pk):
    comment = get_object_or_404(
        Comment.objects.select_related('parent_thread__college'),
        pk=comment_pk
    )
    thread = comment.parent_thread
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
        pressed_like = json.loads(request.POST['pressed_like'])
        if not isinstance(pressed_like, bool):
            msg = """ Sorry, something went wrong with trying to like the
                comment! Please try again in a few minutes. """
            messages.error(request, msg, extra_tags='alert-error')
        else:
            result = {
                'success': True,
                'likeStatus': handle_comment_like(user, comment, pressed_like),
                'score': comment.score
            }
            return HttpResponse(
                json.dumps(result),
                content_type='application/json'
            )


def handle_comment_like(voter, comment, pressed_like):
    vote = get_vote(voter=voter, vote_class=CommentVote, foreign_key=comment)
    # if user hasn't voted, then the returned vote from get_vote() would
    # not be commited to the database yet, and not have a primary key yet
    like_status = 0
    if vote.pk is not None:
        like_status = 1 if vote.is_upvote else -1

    if like_status == -1:
        if pressed_like:  # switches from dislike to like
            vote.is_upvote = True
            vote.save()
            comment.score += 2
            like_status = 1
        else:  # toggles off dislike
            vote.delete()
            comment.score += 1
            like_status = 0
    elif like_status == 0:  # like or dislikes for the first time
        vote.is_upvote = pressed_like
        vote.save()
        comment.score = comment.score + 1 if pressed_like else comment.score - 1
        like_status = 1 if pressed_like else -1
    elif like_status == 1:
        if pressed_like:  # toggles off like
            vote.delete()
            comment.score -= 1
            like_status = 0
        else:  # switches from like to dislike
            vote.is_upvote = False
            vote.save()
            comment.score -= 2
            like_status = -1
    
    comment.save()
    return like_status


def get_vote(voter, vote_class, foreign_key):
    vote_class_kwargs = {'voter': voter}
    vote_class_kwargs['comment'] = foreign_key

    try:
        curr_vote = vote_class.objects.get(**vote_class_kwargs)
        return curr_vote
    except vote_class.DoesNotExist:
        vote_class_kwargs['is_upvote'] = True
        new_vote = vote_class(**vote_class_kwargs)
        return new_vote
