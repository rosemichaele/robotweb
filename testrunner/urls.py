from django.urls import path

from . import views

app_name = 'testrunner'
urlpatterns = [
    path('', views.index, name='index'),
    # All applications available to test will be listed on the testrunner index page.
    path('applications/', views.ApplicationListView.as_view(), name='application-list'),
    # This view will give details about the application and its test suites.
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application-detail'),
    # This view will give details about test suites, along with any child suites and tests. An optional query parameter
    # ``parent`` is supported to limit the suites that are displayed on a given page (defaults to root test suite.)
    path('applications/<int:pk>/suites/', views.SuiteListView.as_view(), name='suite-list'),
    # This view will give details about the test suite.
    path('applications/<int:app_id>/suites/<int:pk>/', views.SuiteDetailView.as_view(), name='suite-detail'),
    # This view will give details about the tests in a certain suite and allow them to be run.
    path('applications/<int:app_id>/suites/<int:pk>/tests/', views.TestListView.as_view(), name='test-list'),
    # This view will give details about the test.
    path('applications/<int:app_id>/suites/<int:suite_id>/tests/<int:pk>/',
         views.TestDetailView.as_view(),
         name='test-detail'),
    path('tests/<int:pk>/run', views.run_test, name='run-test'),
    # This view will be displayed when a test run is submitted successfully.
    path('success', views.run_success, name='run-success'),
]
