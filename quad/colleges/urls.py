from django.urls import path, include

from .views import (
    view_forum,
    create_thread,
    view_thread,
    create_comment,
    reply_comment,
    like_thread,
)


urlpatterns = [
    path('<slug:college_slug>', view_forum, name='forum'),
    path('<slug:college_slug>/new', create_thread, name='new_thread'),
    path('thread/<slug:thread_slug>', view_thread, name='thread'),
    path('thread/<slug:thread_slug>/like', like_thread, name='like_thread'),
    path('thread/<slug:thread_slug>/new', create_comment, name='new_comment'),
    path('thread/<int:comment_pk>/reply', reply_comment, name='reply_comment'),
]
