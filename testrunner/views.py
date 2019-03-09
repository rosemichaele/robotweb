from django.shortcuts import get_object_or_404, render
from django.views import generic
from .models import RobotApplicationUnderTest, RobotTestSuite, RobotTest


def index(request):
    template_name = 'testrunner/index.html'
    return render(request, template_name=template_name)


class ApplicationListView(generic.ListView):
    template_name = 'testrunner/application_list.html'
    context_object_name = 'active_apps'

    def get_queryset(self):
        """Return all active applications."""
        return RobotApplicationUnderTest.objects.filter(active=True)


class ApplicationDetailView(generic.DetailView):
    model = RobotApplicationUnderTest
    template_name = 'testrunner/application.html'


class SuiteListView(generic.ListView):
    template_name = 'testrunner/suite_list.html'
    context_object_name = 'suites'
    application = None
    parent = None

    def get_queryset(self):
        parent_verbose = self.request.GET.get('parent')
        if parent_verbose is not None:
            self.parent = [suite for suite in RobotTestSuite.objects.all()
                           if suite.verbose_name.lower() == parent_verbose.lower()][0]
        else:
            self.parent = RobotTestSuite.objects.get(parent=None)
        self.application = get_object_or_404(RobotApplicationUnderTest, pk=self.kwargs['pk'])
        active_app_suites = RobotTestSuite.objects.filter(active=True,
                                                          application=self.application,
                                                          parent=self.parent)
        return active_app_suites

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app'] = self.application
        context['parent'] = self.parent
        return context


class SuiteDetailView(generic.DetailView):
    model = RobotTestSuite
    template_name = 'testrunner/suite.html'


class TestListView(generic.ListView):
    template_name = 'testrunner/test_list.html'
    context_object_name = 'tests'
    application = None
    test_suite = None

    def get_queryset(self):
        self.test_suite = get_object_or_404(RobotTestSuite, pk=self.kwargs['pk'])
        self.application = self.test_suite.application
        active_suite_tests = RobotTest.objects.filter(active=True,
                                                      robot_suite=self.test_suite)
        return active_suite_tests

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app'] = self.application
        context['suite'] = self.test_suite
        return context


class TestDetailView(generic.DetailView):
    model = RobotTest
    template_name = 'testrunner/test.html'
