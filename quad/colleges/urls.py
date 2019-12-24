from django.urls import path, include

from .views import ForumView, ThreadCreateView


urlpatterns = [
    path('<slug:slug>', ForumView.as_view(), name='forum'),
    path('<slug:slug>/new', ThreadCreateView.as_view(), name='new_thread'),
]
