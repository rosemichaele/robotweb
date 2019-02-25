from robot.api import TestData
from robot.errors import DataError
from robot.parsing.model import TestCase
from django.db.utils import IntegrityError

from testrunner.models import RobotApplicationUnderTest, RobotTestSuite, RobotTest

from .exceptions import RobotDiscoveryException


class DiscoveredRobotApplication:

    def __init__(self, robot_app: RobotApplicationUnderTest):
        """
        After an application for testing has been defined using the testrunner app, use this discovery utility
        to identify Robot test suites and test cases contained in the applications root suite directory.
        :param robot_app: An existing instance of testrunner application under test with a valid, accessible
        ``app_test_location`` attribute.
        """
        self.app = robot_app
        self.name = robot_app.name
        self.source = robot_app.app_test_location
        self.root_suite = None
        try:
            self.robot_test_data = TestData(source=robot_app.app_test_location)
        except (TypeError, PermissionError, DataError) as e:
            raise RobotDiscoveryException('There was an issue accessing data in the test location for this application.'
                                          ' Make sure it was created correctly. The error message was: ' + str(e))
        self.test_suites = list()   # list of DiscoveredRobotTestSuite

    def discover_suites_and_tests(self):
        """
        Recursively discover all child test suites (directory or file-based) for this application. This function assumes
        that the configured ``app_test_location`` of ``robot_app`` is the root directory containing all Robot tests for
        it.
        """
        self.root_suite = DiscoveredRobotTestSuite(discovered_robot_app=self, suite_test_data=self.robot_test_data)
        self.test_suites.append(self.root_suite)
        self.root_suite.discover_child_suites_and_tests()

    def configure_suites_and_tests(self):
        """After discovery and validation, save all child suites and their tests for access in the RobotWeb site."""
        if self.root_suite is None:
            raise RobotDiscoveryException('Tests and suites must be discovered before they can be configured.')
        else:
            self.root_suite.configure()

    def remove_discovered_test_suite(self, verbose_suite_name):
        """Remove a test suite from the discovered list if it should not be configured in RobotWeb."""
        self.test_suites = [s for s in self.test_suites if not s.name.startswith(verbose_suite_name)]
        for r_suite in self.test_suites:
            r_suite.remove_discovered_child_suite(verbose_suite_name)

    def __str__(self):
        return 'DiscoveredRobotApplication: ' + self.name

    def __repr__(self):
        return str(self)


class DiscoveredRobotTestSuite:

    def __init__(self,
                 discovered_robot_app: DiscoveredRobotApplication=None,
                 suite_test_data: TestData=None,
                 robot_suite: RobotTestSuite = None,
                 _parent=None):
        """
        There are two options for using this object:

        (1) A new application has been created in RobotWeb and no tests or test suites have been configured to run
            against the app. In this case, pass an instance of DiscoveredRobotApplication along with its
             ``robot_test_data`` attribute.  A shortcut for this is provided via the discover_suites_and_tests
             instance method of DiscoveredRobotApplication.
        (2) An existing application and test suites have been created and configured in RobotWeb, but changes or
            additions have been made to the source that need to be loaded. In this case, pass an instance of
            RobotTestSuite to __init__ that represents the top-level Robot test suite under which all changes have been
            made. It is only necessary to do this if tests or suites have been added, removed or renamed.

        :param discovered_robot_app: conditionally required if setting up an application for testing with RobotWeb for
        the first time. An instance of DiscoveredRobotApplication. If not provided, ``robot_suite`` is required.
        :param suite_test_data: conditionally required if setting up an application for testing with RobotWeb for
        the first time. An instance of robot.api.TestData that describes the root test suite for all application tests.
        If not provided, ``robot_suite`` is required.
        :param robot_suite: An instance of testrunner.models.RobotTestSuite that describes an existing Robot test suite
        that needs to be refactored. NOTE: if robot_suite is provided, ``discovered_robot_app`` and ``suite_test_data``
        will be ignored.
        :param _parent: Internal attribute that is used to track the naming of child tests and suites during discovery.
        This is another instance of DiscoveredRobotTestSuite.
        """
        if robot_suite and robot_suite.suite_location:
            self.discovered_app = DiscoveredRobotApplication(robot_suite.application)
            self.suite_test_data = TestData(source=robot_suite.suite_location)
            self.name = robot_suite.verbose_name
        elif robot_suite and not robot_suite.suite_location:
            raise RobotDiscoveryException('The RobotTestSuite has no associated location on the file system. No tests '
                                          'can be discovered until that information is supplied.')
        elif not (discovered_robot_app and suite_test_data):
            raise RobotDiscoveryException('This appears to be a discovery attempt for a newly created application under'
                                          ' test, but instances of a DiscoveredRobotApplication AND robot TestData were'
                                          ' not supplied. This is required.')
        else:
            self.discovered_app = discovered_robot_app
            self.suite_test_data = suite_test_data
            if _parent is None:
                self.name = suite_test_data.name
            else:
                self.name = _parent.name + '.' + self.suite_test_data.name
        self.documentation = self.suite_test_data.setting_table.doc.value
        self.location = self.suite_test_data.source
        self.child_suites = list()  # list of DiscoveredRobotTestSuite
        self.tests = list()     # list of DiscoveredRobotTest

    def discover_child_suites_and_tests(self):
        """Discover all tests in the suite's location, then recursively discover child suites and their tests."""
        self._discover_tests()
        for child_suite in self.suite_test_data.children:
            discovered_child = DiscoveredRobotTestSuite(self.discovered_app, child_suite, _parent=self)
            self.discovered_app.test_suites.append(discovered_child)
            self.child_suites.append(discovered_child)
        for child in self.child_suites:
            child.discover_child_suites_and_tests()

    def _discover_tests(self):
        """Compile the list of Robot test cases that belong to this test suite."""
        for test in self.suite_test_data.testcase_table:
            discovered_test = DiscoveredRobotTest(test, self)
            self.tests.append(discovered_test)

    def configure(self):
        """
        Create a RobotTestSuite for the discovered test suite if one does not already exist, then configure tests
        and recursively configure any child test suites.
        """
        if self.name == self.suite_test_data.name:
            parent = None
            name = self.name
            if len(RobotTestSuite.objects.filter(name=name, parent=parent, application=self.discovered_app.app)) > 0:
                print('(Continuing) Root test suite already exists.')
                self._configure_tests()
                self._configure_child_suites_and_tests()
                return  # Don't create root test suite since one already exists. Necessary because in SQL, NULL != NULL
        else:
            parent = self._get_existing_parent_suite()
            name = self.name.split('.')[-1]
        print('Configuring test suite: ' + self.name)
        configurable_suite = RobotTestSuite(name=name,
                                            documentation=self.documentation,
                                            parent=parent,
                                            application=self.discovered_app.app,
                                            suite_location=self.location)
        try:
            configurable_suite.save()
            print('Added test suite: ' + configurable_suite.verbose_name)
        except IntegrityError:
            print('(Skipped) Existing test suite found with the same name and parent suite for {app}: '
                  '{v}'.format(app=self.discovered_app.app, v=configurable_suite.verbose_name))
        self._configure_tests()
        self._configure_child_suites_and_tests()

    def _configure_child_suites_and_tests(self):
        if not self.child_suites:
            print('(Continuing) No child suites to configure for: ' + self.name)
        for child in self.child_suites:
            child.configure()

    def _configure_tests(self):
        for test in self.tests:
            test.configure()

    def remove_discovered_child_suite(self, verbose_suite_name):
        """Remove a child test suite from the discovered list if it should not be configured in RobotWeb."""
        self.child_suites = [s for s in self.child_suites if not s.name.startswith(verbose_suite_name)]
        self.discovered_app.test_suites = [ts for ts in self.discovered_app.test_suites
                                           if not ts.name.startswith(verbose_suite_name)]

    def remove_discovered_test(self, test_name):
        """Remove a test with the given name from the discovered tests, so it won't be configured."""
        self.tests = [t for t in self.tests if t.name != test_name]

    def _get_existing_parent_suite(self):
        parent_name = '.'.join(self.name.split('.')[:-1])
        try:
            return [s for s in RobotTestSuite.objects.all() if s.verbose_name == parent_name][0]
        except IndexError:
            raise AssertionError('There should have been an existing parent suite, but one was not found. Tried to '
                                 'find a test suite with this verbose/display name: ' + parent_name)

    def __str__(self):
        return 'DiscoveredRobotTestSuite: ' + self.name

    def __repr__(self):
        return str(self)


class DiscoveredRobotTest:

    def __init__(self, test: TestCase, discovered_suite: DiscoveredRobotTestSuite):
        self.name = test.name
        self.discovered_suite = discovered_suite
        self.documentation = test.doc.value

    def configure(self):
        """Create a RobotTest for this discovered test case."""
        print('Configuring test: ' + self.name)
        configurable_test = RobotTest(name=self.name,
                                      documentation=self.documentation,
                                      robot_suite=self._get_existing_robot_suite())
        try:
            configurable_test.save()
            print('Added test: ' + configurable_test.verbose_name)
        except IntegrityError:
            print('(Skipped) There is an existing test with the same name and parent suite for {app}: '
                  '{v}'.format(v=configurable_test.verbose_name, app=self.discovered_suite.discovered_app.app))

    def _get_existing_robot_suite(self):
        try:
            return [s for s in RobotTestSuite.objects.all() if s.verbose_name == self.discovered_suite.name][0]
        except IndexError:
            raise AssertionError('There should have been an existing test suite for this test, but one was not found.')

    def __str__(self):
        return 'DiscoveredRobotTest: ' + self.name

    def __repr__(self):
        return str(self)
