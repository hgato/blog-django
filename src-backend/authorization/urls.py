from django.urls import path

from . import views

urlpatterns = [
    path('', views.UserView.as_view(), name='user'),
    path('check', views.check, name='check_user'),
    path('logout', views.logout, name='logout')
]
