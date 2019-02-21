from robot.api import TestData
from testrunner.models import RobotApplicationUnderTest, RobotTestSuite, RobotTest


def create_robotweb_objects(app, suite, parent_verbose=None):
    try:
        parent_suite = [s for s in RobotTestSuite.objects.all() if s.verbose_name == parent_verbose][0]
    except IndexError:
        parent_suite = None
    new_suite = RobotTestSuite(name=suite.name,
                               application=app,
                               documentation=suite.setting_table.doc.value,
                               parent=parent_suite,
                               suite_location=suite.source)
    new_suite.save()
    for test in suite.testcase_table:
        new_test = RobotTest(name=test.name,
                             robot_suite=new_suite,
                             documentation=test.doc.value)
        new_test.save()
    for child in suite.children:
        create_robotweb_objects(app, child, parent_verbose=new_suite.verbose_name)
