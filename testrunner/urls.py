from django.urls import path

from . import views

app_name = 'testrunner'
urlpatterns = [
    path('', views.index, name='index'),
]