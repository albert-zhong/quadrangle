from django.urls import path, include

from .views import (
    view_forum,
    create_thread,
    view_thread,
    edit_thread,
    delete_thread,
    create_comment,
    edit_comment,
    delete_comment,
    reply_comment,
    like_thread,
    like_comment,
)


urlpatterns = [
    path('<slug:college_slug>', view_forum, name='forum'),
    path('<slug:college_slug>/new', create_thread, name='new_thread'),
    path('thread/<slug:thread_slug>', view_thread, name='thread'),
    path('thread/<slug:thread_slug>/edit', edit_thread, name='edit_thread'),
    path('thread/<slug:thread_slug>/delete', delete_thread, name='delete_thread'),
    path('thread/<slug:thread_slug>/like', like_thread, name='like_thread'),
    path('comments/<slug:thread_slug>/new', create_comment, name='new_comment'),
    path('comments/<int:comment_pk>/edit', edit_comment, name='edit_comment'),
    path('comments/<int:comment_pk>/delete', delete_comment, name='delete_comment'),
    path('comments/<int:comment_pk>/reply', reply_comment, name='reply_comment'),
    path('comments/<int:comment_pk>/like', like_comment, name='like_comment'),
]
