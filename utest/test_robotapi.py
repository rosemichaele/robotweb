import os
from django.test import TestCase
from testrunner.models import RobotApplicationUnderTest
from robotapi.discover import DiscoveredRobotTest, DiscoveredRobotTestSuite, DiscoveredRobotApplication

sep = os.path.sep
HERE = os.path.realpath(__file__)
TEST_ROBOT_APP_DIR = sep.join(HERE.split(sep)[:-1]) + sep + 'TestRobotAppSuite'


class TestDiscovery(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('Running robotapi unit tests in: ' + HERE)
        print('Robot dummy test suite located here: ' + TEST_ROBOT_APP_DIR)
        # Create a dummy RobotApplicationUnderTest object saved in the test database (in memory for SQLite3)
        cls.test_robot_app = RobotApplicationUnderTest.objects.create(name='My Test Robot App',
                                                                      description='An application created for testing '
                                                                                  'RobotWeb discovery tools.',
                                                                      robot_location=HERE,
                                                                      app_test_location=TEST_ROBOT_APP_DIR)
        cls.bad_robot_app = RobotApplicationUnderTest.objects.create(name='My Test Robot App',
                                                                     description='An application created for testing '
                                                                                 'RobotWeb discovery tools.',
                                                                     robot_location=HERE,
                                                                     app_test_location='')
        cls.discovered_app = DiscoveredRobotApplication(cls.test_robot_app)

    def test_discovered_robot_app_creation(self):
        self.assertEqual(self.discovered_app.app, self.test_robot_app)
        self.assertEqual(self.discovered_app.name, self.test_robot_app.name)
        self.assertEqual(self.discovered_app.source, self.test_robot_app.app_test_location)
        self.assertIsNone(self.discovered_app.root_suite)
        self.assertEqual(self.discovered_app.test_suites, [])
        self.assertEqual(repr(self.discovered_app), 'DiscoveredRobotApplication: ' + self.test_robot_app.name)

    def test_bad_app_test_location_raises(self):
        with self.assertRaisesMessage(AssertionError, 'There was an issue accessing data in the test location for this '
                                                      'application. Make sure it was created correctly. The error '
                                                      'message was: '):
            DiscoveredRobotApplication(self.bad_robot_app)

    def test_must_be_discovered_before_configured(self):
        with self.assertRaisesMessage(AssertionError, 'Tests and suites must be discovered before '
                                                      'they can be configured.'):
            self.discovered_app.configure_suites_and_tests()
