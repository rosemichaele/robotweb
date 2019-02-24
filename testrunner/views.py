from urllib.parse import unquote

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404

from .models import RobotApplicationUnderTest, RobotTestSuite, RobotTest


class ViewFinder:
    """Helper methods to find related Robot records from URL context."""
    @classmethod
    def get_app_or_404(cls, app_name: str):
        """
        Returns an active RobotApplicationUnderTest object based on the provided name, escaping any encoded characters
        from the URL. If no match, return a Django Http404 object.
        """
        return get_object_or_404(RobotApplicationUnderTest, active=True, name=unquote(app_name))

    @classmethod
    def get_suite_or_404(cls, app: RobotApplicationUnderTest, suite_name: str):
        """
        Returns an active RobotTestSuite object based on the provided suite name and RobotApplicationUnderTest, 
        escaping any encoded characters from the URL. If no match, return a Django Http404 object.
        """
        verbose_suite_name = '.'.join([n for n in unquote(suite_name).split('.')])
        try:
            matched_suite = [s for s in RobotTestSuite.objects.filter(active=True, application=app)
                             if s.verbose_name == verbose_suite_name][0]
        except IndexError:
            raise Http404('No suite with verbose name {name} in the {app} application.'.format(name=verbose_suite_name,
                                                                                               app=app.name))
        return matched_suite

    @classmethod
    def get_test_or_404(cls, matched_suite: RobotTestSuite, test_name: str):
        """
        Returns an active RobotTest object based on the provided test name and RobotTestSuite, escaping any encoded
        characters from the URL. If no match, return a Django Http404 object.
        """
        return get_object_or_404(RobotTest, active=True, robot_suite=matched_suite, name=test_name)


def index(request):
    return HttpResponse('<h3>Select an application to test below.</h3>'
                        '<ul>{apps}</ul>'.format(apps=''.join(['<li><a href="applications/{app}">{app}</a></li>'.
                                                              format(app=app.name)
                                                              for app in RobotApplicationUnderTest.objects.all()])))


def application(request, application_name):
    app = ViewFinder.get_app_or_404(application_name)
    return HttpResponse('This page will show the {name} application view.'.format(name=app.name))


def suite(request, application_name, suite_name):
    app = ViewFinder.get_app_or_404(application_name)
    matched_suite = ViewFinder.get_suite_or_404(app, suite_name)
    return HttpResponse('This page will show information about the {suite} test suite for {app}.'
                        .format(suite=matched_suite.verbose_name, app=app.name))


def test(request, application_name, suite_name, test_name):
    app = ViewFinder.get_app_or_404(application_name)
    matched_suite = ViewFinder.get_suite_or_404(app, suite_name)
    matched_test = ViewFinder.get_test_or_404(matched_suite, test_name)
    return HttpResponse('This page will show information about the {test} test '
                        'in the {suite} test suite of the {app} application'.format(test=matched_test.name,
                                                                                    suite=matched_suite.verbose_name,
                                                                                    app=app.name))
