import os
from django.test import TestCase
from robot.parsing.model import TestDataDirectory, TestCaseFile

from testrunner.models import RobotApplicationUnderTest
from robotapi.discover import DiscoveredRobotTest, DiscoveredRobotTestSuite, DiscoveredRobotApplication
from robotapi.exceptions import RobotDiscoveryException

SEP = os.path.sep
HERE = os.path.realpath(__file__)
UTEST_ROOT = SEP.join(HERE.split(SEP)[:-1])
TEST_ROBOT_APP_DIR = SEP.join(HERE.split(SEP)[:-1]) + SEP + 'TestRobotAppSuite'
TEST_SUITE_NAME_KEY = {  # name : verbose_name - if any are added or changed this also needs to be updated
    'TestRobotAppSuite': 'TestRobotAppSuite',
    'RobotAppSubDirectory': 'TestRobotAppSuite.RobotAppSubDirectory',
    'AppSubSuite1': 'TestRobotAppSuite.AppSubSuite1',
    'AppSubSuite2': 'TestRobotAppSuite.AppSubSuite2',
    'NestedChildSuite': 'TestRobotAppSuite.RobotAppSubDirectory.NestedChildSuite',
    'TemplateSubSuite': 'TestRobotAppSuite.RobotAppSubDirectory.TemplateSubSuite',
    'AnotherTemplateTestSuite': 'TestRobotAppSuite.RobotAppSubDirectory.AnotherTemplateTestSuite',
    'NestedTestSuite GivenWhenThen': 'TestRobotAppSuite.RobotAppSubDirectory.NestedChildSuite.'
                                     'NestedTestSuite GivenWhenThen',
}
TEST_SUITE_DOC_KEY = {  # verbose_name : doc - if any are added or changed this also needs to be updated
    'TestRobotAppSuite': '',
    'TestRobotAppSuite.RobotAppSubDirectory': '',
    'TestRobotAppSuite.AppSubSuite1': 'A test suite with a single test for valid login.\\n\\n'
                                      'This test has a workflow that is created using keywords in\\n'
                                      'the imported resource file.',
    'TestRobotAppSuite.AppSubSuite2': 'Example using the space separated plain text format.',
    'TestRobotAppSuite.RobotAppSubDirectory.NestedChildSuite': '',
    'TestRobotAppSuite.RobotAppSubDirectory.TemplateSubSuite': '',
    'TestRobotAppSuite.RobotAppSubDirectory.AnotherTemplateTestSuite': '',
    'TestRobotAppSuite.RobotAppSubDirectory.NestedChildSuite.NestedTestSuite GivenWhenThen': '',
}


class TestDiscovery(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('Running robotapi discovery unit tests in: ' + HERE)
        print('Dummy Robot test suite located here: ' + TEST_ROBOT_APP_DIR)
        # Create a dummy RobotApplicationUnderTest object saved in the test database (in memory for SQLite3)
        cls.test_robot_app = RobotApplicationUnderTest.objects.create(name='My Test Robot App',
                                                                      description='An application created for testing '
                                                                                  'RobotWeb discovery tools.',
                                                                      robot_location=HERE,
                                                                      app_test_location=TEST_ROBOT_APP_DIR)
        cls.bad_robot_app = RobotApplicationUnderTest.objects.create(name='My Bad Test Robot App',
                                                                     description='An application created for testing '
                                                                                 'unhappy RobotWeb discovery tools.',
                                                                     robot_location=HERE,
                                                                     app_test_location='')

    def test_discovered_robot_app_creation(self):
        # Expected attribute values after application under test is discovered
        discovered_app = DiscoveredRobotApplication(self.test_robot_app)
        self.assertEqual(discovered_app.app, self.test_robot_app)
        self.assertEqual(discovered_app.name, 'My Test Robot App')
        self.assertEqual(discovered_app.source, TEST_ROBOT_APP_DIR)
        self.assertIsNone(discovered_app.root_suite)
        self.assertEqual(discovered_app.test_suites, [])
        self.assertEqual(repr(discovered_app), 'DiscoveredRobotApplication: ' +  'My Test Robot App')

    def test_bad_app_test_location_raises(self):
        with self.assertRaisesMessage(RobotDiscoveryException, 'There was an issue accessing data in the test location '
                                                               'for this application. Make sure it was created '
                                                               'correctly. The error message was: '):
            DiscoveredRobotApplication(self.bad_robot_app)

    def test_root_app_suite_discovery(self):
        discovered_app = DiscoveredRobotApplication(self.test_robot_app)
        discovered_app.discover_suites_and_tests()
        self.assertEqual(discovered_app.root_suite.name, 'TestRobotAppSuite')
        self.assertIsInstance(discovered_app.root_suite, DiscoveredRobotTestSuite)
        self.assertIsInstance(discovered_app.root_suite.suite_test_data, TestDataDirectory)
        self.assertEqual(discovered_app.root_suite.documentation, '')   # This is a directory and has no documentation.
        self.assertEqual(discovered_app.root_suite.location, TEST_ROBOT_APP_DIR)
        self.assertEqual(discovered_app.root_suite.tests, [])   # This is a directory and has no direct child tests.

    def test_child_suites_discovery(self):
        discovered_app = DiscoveredRobotApplication(self.test_robot_app)
        discovered_app.discover_suites_and_tests()
        self.assertEqual(len(discovered_app.test_suites), 8)  # Total test suites discovered including the root suite.
        actual_test_count = 0
        for s in discovered_app.test_suites:
            file_extension = ''
            if not isinstance(s.suite_test_data, TestDataDirectory):    # Then it must be a TestCaseFile
                file_extension = '.' + s.suite_test_data.source.split('.')[-1]
            verbose_name_parts = s.name.split('.')
            verbose_name_file_parts = [p.replace(' ', '_') for p in verbose_name_parts]
            self.assertEqual(TEST_SUITE_NAME_KEY.get(verbose_name_parts[-1]), s.name)
            self.assertEqual(s.location, UTEST_ROOT + SEP + SEP.join(verbose_name_file_parts) + file_extension)
            self.assertEqual(TEST_SUITE_DOC_KEY.get(s.name), s.documentation)
            actual_test_count += len(s.tests)
        self.assertEqual(actual_test_count, 15)


class TestConfiguration(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('Running robotapi configuration unit tests in: ' + HERE)
        print('Dummy Robot test suite located here: ' + TEST_ROBOT_APP_DIR)
        # Create a dummy RobotApplicationUnderTest object saved in the test database (in memory for SQLite3)
        cls.test_robot_app = RobotApplicationUnderTest.objects.create(name='My Test Robot App',
                                                                      description='An application created for testing '
                                                                                  'RobotWeb discovery tools.',
                                                                      robot_location=HERE,
                                                                      app_test_location=TEST_ROBOT_APP_DIR)

    def test_suites_must_be_discovered_before_configured(self):
        discovered_app_suites_not_discovered = DiscoveredRobotApplication(self.test_robot_app)
        with self.assertRaisesMessage(RobotDiscoveryException, 'Tests and suites must be discovered before '
                                                               'they can be configured.'):
            discovered_app_suites_not_discovered.configure_suites_and_tests()
