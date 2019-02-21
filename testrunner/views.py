from urllib.parse import unquote

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .models import RobotApplicationUnderTest, RobotTestSuite


def index(request):
    return HttpResponse('<h3>Select an application to test below.</h3>'
                        '<ul>{apps}</ul>'.format(apps=''.join(['<li><a href="applications/{app}">{app}</a></li>'.
                                                              format(app=app.name)
                                                              for app in RobotApplicationUnderTest.objects.all()])))


def application(request, application_name):
    app = get_object_or_404(RobotApplicationUnderTest,
                            active=True,
                            name=unquote(application_name))
    return HttpResponse('This page will show the {name} application view.'.format(name=app.name))


def suite(request, application_name, suite_name):
    app = get_object_or_404(RobotApplicationUnderTest,
                            name=unquote(application_name))
    suites_list = [unquote(n) for n in suite_name.split('~')]
    root_suite = get_object_or_404(RobotTestSuite,
                                   active=True,
                                   name=suites_list[0],
                                   application=app)
    names = [root_suite.name]
    current_parent = root_suite
    if len(suites_list) == 1:
        pass
    else:
        for test_suite_name in suites_list[1:]:
            next_suite = get_object_or_404(RobotTestSuite,
                                           active=True,
                                           name=test_suite_name,
                                           parent=current_parent)
            names.append(next_suite.name)
            current_parent = next_suite
    return HttpResponse('This page will show information about the {suite} test suite for {app}.'
                        .format(suite='~'.join(names), app=root_suite.application.name))


def test(request):
    return HttpResponse('This content will show in the test view.')