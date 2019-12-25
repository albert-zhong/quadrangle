from django.urls import path, include

from .views import ForumView, ThreadCreateView, ThreadListView


urlpatterns = [
    path('<slug:college_slug>', ForumView.as_view(), name='forum'),
    path('<slug:college_slug>/new', ThreadCreateView.as_view(), name='new_thread'),
    path('<slug:college_slug>/<slug:thread_slug>', ThreadListView.as_view(), name='thread_list'),
]
