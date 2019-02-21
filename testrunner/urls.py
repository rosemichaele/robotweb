from django.urls import path

from . import views

app_name = 'testrunner'
urlpatterns = [
    path('', views.index, name='index'),
    # All applications available to test will be listed on the testrunner index page.
    path('applications/<str:application_name>/', views.application, name='application'),
    # This view will give details about the application and its test suites.
    path('applications/<str:application_name>/<str:suite_name>/', views.suite, name='suite'),
    # This view will give details about test suites, along with any child suites and tests.
]
