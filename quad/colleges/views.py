from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

import json
from .forms import ThreadForm, ThreadEditForm, CommentForm, CommentEditForm
from .messages import alert
from .models import (
    College,
    Thread,
    Comment,
    ThreadVote,
    CommentVote,
    AnonymousName,
)


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
    threads = college.threads.all().select_related('author')
    names = {
        thread.slug: get_display_name(user=request.user, post=thread) for thread in threads
    }
    context = {
        'college': college,
        'threads': threads,
        'names': names,
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
            AnonymousName.objects.get_or_create(user=user, thread=new_thread)
            alert(request, 'Thread successfully created!', 'success')
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
    author = thread.author
    college = thread.college
    user = request.user

    if not user_belongs(request, college):
        return redirect('home')

    # Preprocesses author display names for comments and thread
    # Names maps every comment PK or 'thread' to its corresponding display name
    anons = AnonymousName.objects.filter(thread=thread)
    anon_names = {anon.user: f'[anonymous {anon.id}]' for anon in anons}
    comments = thread.comments.all().select_related('author')
    names = {
        comment.pk: get_display_name(user=user, post=comment, anon_names=anon_names) for comment in comments
    }
    names['thread'] = get_display_name(user=user, post=thread, anon_names=anon_names)

    comment_like_statuses = {
        comment.pk: {'score': comment.score, 'likeStatus': 0} for comment in comments
    }

    for vote in user.commentvote_votes.prefetch_related('voter'):
        pk = vote.comment.pk
        is_like = vote.is_like
        if pk in comment_like_statuses:
            comment_like_statuses[pk]['likeStatus'] = 1 if is_like else -1

    template_name = 'forum/thread.html'
    context = {
        'college': college,
        'thread': thread,
        'names': names,
        'comments': comments,
        'thread_like_status': get_like_status(user, ThreadVote, thread),
        'comment_like_statuses': comment_like_statuses
    }

    return render(request, template_name, context)


def get_display_name(user, post, anon_names={}):
    author = post.author
    
    if author == user:
        return '[me]'
    elif not author:
        return '[deleted]'
    elif post.is_anonymous:
        if author in anon_names:
            return anon_names[author]
        return '[anonymous]'
    
    return author


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
        thread.author = None
        thread.title = '[deleted]'
        thread.body = '[deleted]'
        thread.save()
        alert(request, 'Thread successfully deleted!', 'success')
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
        Thread.objects.select_related('author'),
        slug=thread_slug
    )
    user = request.user

    author = thread.author
    if not user_owns(request, author):
        return redirect(thread)
        
    if request.method == 'POST':
        form = ThreadEditForm(request.POST)
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
    form = ThreadEditForm(initial=initial_values)
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
            AnonymousName.objects.get_or_create(user=user, thread=thread)
            thread.comments_count += 1
            thread.save()
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
        Comment.objects.select_related('thread__college'),
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
            thread.comments_count += 1
            thread.save()
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
def edit_comment(request, comment_pk):
    comment = get_object_or_404(
        Comment.objects.select_related('author', 'thread'),
        pk=comment_pk
    )
    author = comment.author
    thread = comment.thread
    user = request.user

    if user != comment.author:
        alert(request, 'You can only edit your own comments!', 'warning')
        return redirect('home')

    if request.method == 'POST':
        form = CommentEditForm(request.POST)
        if form.is_valid():
            comment.body = form.cleaned_data['body']
            comment.save()
            alert(request, 'Comment successfully updated!', 'success')
            return redirect(thread)
        else:
            alert(request, 'Something went wrong with creating that comment. ' +
                'Please try again in a few minutes!', 'error')

    template_name = 'forum/new_comment.html'
    form = CommentEditForm(initial={'body': comment.body})
    context = {'form': form}

    return render(request, template_name, context)


@login_required
def delete_comment(request, comment_pk):
    comment = get_object_or_404(
        Comment.objects.select_related('author', 'thread'),
        pk=comment_pk
    )
    author = comment.author
    thread = comment.thread
    user = request.user

    if user != comment.author:
        alert(request, 'You can only edit your own comments!', 'warning')
        return redirect('home')

    if request.method == 'POST':
        comment.author = None
        comment.body = '[deleted]'
        comment.save()
        alert(request, 'Comment successfully deleted!', 'success')
        return redirect(thread)

    template_name = 'forum/delete_comment.html'
    context = {
        'node': comment
    }
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
    
    has_liked = json.loads(request.POST['hasLiked'])
    data = {'success': False}

    if isinstance(has_liked, bool):
        data = {
            'success': True,
            'likeStatus': update_like_status(user, ThreadVote, thread, has_liked),
            'newScore': thread.score
        }

    return HttpResponse(json.dumps(data), content_type='application/json')


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

    has_liked = json.loads(request.POST['hasLiked'])
    if isinstance(has_liked, bool):
        result = {
            'success': True,
            'likeStatus': update_like_status(user, CommentVote, comment, has_liked),
            'newScore': comment.score
        }
        return HttpResponse(
            json.dumps(result),
            content_type='application/json'
        )
