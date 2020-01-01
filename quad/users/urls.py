from django.urls import path, re_path

from .views import SignUpView, activate


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activate, name='activate'),
]