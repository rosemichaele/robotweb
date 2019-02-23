from robot.api import TestData
from robot.errors import DataError
from robot.parsing.model import TestCase

from testrunner.models import RobotApplicationUnderTest


class DiscoveredRobotApplication:

    def __init__(self, robot_app: RobotApplicationUnderTest):
        self.app = robot_app
        self.name = robot_app.name
        self.source = robot_app.app_test_location
        try:
            self.robot_test_data = TestData(source=robot_app.app_test_location)
        except (TypeError, PermissionError, DataError) as e:
            raise AssertionError('There was an issue accessing data in the test location for this application. Make '
                                 'sure it was created correctly. The error message was: ' + str(e))
        self.test_suites = list()   # list of DiscoveredRobotTestSuite

    def discover_test_suites(self):
        root_suite = DiscoveredRobotTestSuite(self, self.robot_test_data)
        self.test_suites.append(root_suite)
        root_suite.discover_tests()
        root_suite.discover_child_suites()

    def __str__(self):
        return 'DiscoveredRobotApplication: ' + self.name

    def __repr__(self):
        return str(self)


class DiscoveredRobotTestSuite:

    def __init__(self, robot_app: DiscoveredRobotApplication, suite_test_data: TestData, parent=None):
        self.app = robot_app
        if parent is None:
            self.name = suite_test_data.name
        else:
            self.name = parent.name + '.' + suite_test_data.name
        self.suite_test_data = suite_test_data
        self.parent = parent
        self.documentation = self.suite_test_data.setting_table.doc.value
        self.location = suite_test_data.source
        self.child_suites = list()  # list of DiscoveredRobotTestSuite
        self.tests = list()     # list of DiscoveredRobotTest

    def discover_child_suites(self):
        self.discover_tests()
        for child_suite in self.suite_test_data.children:
            discovered_child = DiscoveredRobotTestSuite(self.app, child_suite, parent=self)
            self.app.test_suites.append(discovered_child)
            self.child_suites.append(discovered_child)
        for child in self.child_suites:
            child.discover_child_suites()

    def discover_tests(self):
        for test in self.suite_test_data.testcase_table:
            print(test.name)
            discovered_test = DiscoveredRobotTest(test, self)
            self.tests.append(discovered_test)

    def configure(self):
        pass

    def configure_tests(self):
        pass

    def __str__(self):
        return 'DiscoveredRobotTestSuite: ' + self.name

    def __repr__(self):
        return str(self)


class DiscoveredRobotTest:

    def __init__(self, test: TestCase, suite: DiscoveredRobotTestSuite):
        self.name = test.name
        self.suite = suite
        self.documentation = test.doc.value

    def configure(self):
        pass

    def __str__(self):
        return 'DiscoveredRobotTest: ' + self.name

    def __repr__(self):
        return str(self)
