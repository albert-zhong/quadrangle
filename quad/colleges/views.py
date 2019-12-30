from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

import json
from .forms import ThreadForm, CommentForm
from .messages import alert
from .models import College, Thread, Comment, ThreadVote, CommentVote


def user_belongs(request, college):
    if request.user.college == college or request.user.is_staff:
        return True
    alert(request, 'You do not belong to this college.', 'warning')
    return False


def user_owns(request, author):
    return request.user == author or request.user.is_staff


@login_required
def view_forum(request, college_slug):
    college = get_object_or_404(College, slug=college_slug)

    if not user_belongs(request, college):
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

    if not user_belongs(request, college):
        return redirect('home')

    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            new_thread = Thread(
                author=user,
                college=college,
                title=form.cleaned_data['title'],
                body=form.cleaned_data['body'],
                is_anonymous=form.cleaned_data['is_anonymous'],
            )
            new_thread.save()
            alert(request, 'Thread successfully created!')
            return redirect(new_thread)
        else:
            alert(request, 'Something went wrong with creating that thread. ' +
                'Please try again in a few minutes!', 'error')

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

    if not user_belongs(request, college):
        return redirect('home')

    comments = thread.comments.all()

    template_name = 'forum/thread.html'
    context = {
        'college': college,
        'thread': thread,
        'comments': comments,
        'initial_like_status': get_like_status(user, ThreadVote, thread),
    }

    return render(request, template_name, context)


@login_required
def delete_thread(request, thread_slug):
    thread = get_object_or_404(
        Thread.objects.select_related('college', 'author'),
        slug=thread_slug
    )
    college = thread.college
    user = request.user

    if not user_belongs(request, college):
        return redirect('home')

    author = thread.author
    if not user_owns(request, author):
        return redirect(thread)
        
    if request.method == 'POST':
        thread.delete()
        alert(request, 'Thread successfully deleted', 'success')
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

    if not user_belongs(request, college):
        return redirect('home')

    author = thread.author
    if not user_owns(request, author):
        return redirect(thread)
        
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread.title = form.cleaned_data['title']
            thread.body = form.cleaned_data['body']
            thread.save()
            alert(request, 'Thread successfully updated!', 'success')
            return redirect(thread)
        else:
            alert(request, 'Something went wrong with editing that thread. ' +
                'Please try again in a few minutes!', 'error')

    template_name = 'forum/new_thread.html'
    initial_values = {
        'title': thread.title,
        'body': thread.body,
    }
    form = ThreadForm(initial=initial_values)
    context = {'form': form}

    return render(request, template_name, context)


@login_required
def create_comment(request, thread_slug):
    thread = get_object_or_404(
        Thread.objects.select_related('college',),
        slug=thread_slug
    )
    college = thread.college
    user = request.user

    if not user_belongs(request, college):
        return redirect('home')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = Comment(
                author=user,
                thread=thread,
                body=form.cleaned_data['body'],
                is_anonymous=form.cleaned_data['is_anonymous'],
            )
            new_comment.save()
            alert(request, 'Comment successfully created!', 'success')
            return redirect(thread)
        else:
            alert(request, 'Something went wrong with creating that comment. ' +
                'Please try again in a few minutes!', 'error')

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
    thread = parent_comment.thread
    college = thread.college
    user = request.user

    if not user_belongs(request, college):
        return redirect('home')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = Comment(
                author=user,
                thread=thread,
                body=form.cleaned_data['body'],
                is_anonymous=form.cleaned_data['is_anonymous'],
                parent=parent_comment
            )
            new_comment.save()
            alert(request, 'Comment successfully created!', 'success')
            return redirect(thread)
        else:
            alert(request, 'Something went wrong with creating that comment. ' +
                'Please try again in a few minutes!', 'error')

    template_name = 'forum/new_comment.html'
    form = CommentForm()
    context = {'form': form}

    return render(request, template_name, context)


@login_required
@require_POST
def like_thread(request, thread_slug):
    thread = get_object_or_404(
        Thread.objects.select_related('college'),
        slug=thread_slug
    )
    college = thread.college
    user = request.user

    if not user_belongs(request, college):
        return redirect('home')

    pressed = json.loads(request.POST['pressed'])
    if isinstance(pressed, bool):
        result = {
            'success': True,
            'likeStatus': update_like_status(user, ThreadVote, thread, pressed),
            'votes': thread.score
        }
        return HttpResponse(
            json.dumps(result),
            content_type='application/json'
        )


# Returns if the user has disliked (-1), liked (+1), or neither yet (0).
def get_like_status(user, VoteClass, foreign_key):
    like_status = 0
    try:
        kwargs = {'voter': user}
        if isinstance(foreign_key, Thread):
            kwargs['thread'] = foreign_key
        else:
            kwargs['comment'] = foreign_key

        vote = VoteClass.objects.get(**kwargs)
        like_status = 1 if vote.is_like else -1
    except:
        pass

    return like_status


def update_like_status(user, VoteClass, foreign_key, has_liked):
    foreign_keys = {
        ThreadVote: {
            'fk_model': Thread,
            'fk_string': 'thread',
        },
        CommentVote: {
            'fk_model': Comment,
            'fk_string': 'comment',
        }
    }
    if VoteClass not in foreign_keys:
        raise ValueError('Incorrect vote_class')
    if not isinstance(foreign_key, foreign_keys[VoteClass]['fk_model']):
        raise ValueError('Incorrect foreign key for that vote')

    try:
        fk_string = foreign_keys[VoteClass]['fk_string']
        kwargs = {
            'voter': user,
            fk_string: foreign_key,
        }
        curr_vote = VoteClass.objects.get(**kwargs)
        if curr_vote.is_like:
            if has_liked:  # case: hit like once, hit like again to toggle
                like_status = 0
                foreign_key.score -= 1
                curr_vote.delete()
            else:  # case: hit like once, hit dislike
                like_status = -1
                curr_vote.is_like = False
                curr_vote.save()
                foreign_key.score -= 2
        else:
            if has_liked:  # case: hit dislike once, hit like
                like_status = 1
                curr_vote.is_like = True
                curr_vote.save()
                foreign_key.score += 2
            else:  # case: hit dislike once, hit dislike again to toggle
                like_status= 0
                foreign_key.score += 1
                curr_vote.delete()
    except VoteClass.DoesNotExist:
        kwargs['is_like'] = has_liked
        new_vote = VoteClass(**kwargs)
        new_vote.save()
        if has_liked:  # case: hit like once
            like_status = 1
            foreign_key.score += 1
        else:  # case: hit dislike once
            like_status = -1
            foreign_key.score -= 1

    foreign_key.save()
    return like_status


@login_required
@require_POST
def like_comment(request, comment_pk):
    comment = get_object_or_404(
        Comment.objects.select_related('thread__college'),
        pk=comment_pk
    )
    thread = comment.thread
    college = thread.college
    user = request.user

    if not user_belongs(request, college):
        return redirect('home')

    pressed_like = json.loads(request.POST['pressed_like'])
    if isinstance(pressed_like, bool):
        result = {
            'success': True,
            'likeStatus': handle_vote(user, CommentVote, comment, pressed_like),
            'score': comment.score
        }
        return HttpResponse(
            json.dumps(result),
            content_type='application/json'
        )
