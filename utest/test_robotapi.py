import os
from django.test import TestCase
from robot.parsing.model import TestDataDirectory

from testrunner.models import RobotApplicationUnderTest, RobotTestSuite, RobotTest
from robotapi.discover import DiscoveredRobotTest, DiscoveredRobotTestSuite, DiscoveredRobotApplication
from robotapi.exceptions import RobotDiscoveryException

SEP = os.path.sep
HERE = os.path.realpath(__file__)
UTEST_ROOT = SEP.join(HERE.split(SEP)[:-1])
###########################################
# If the example test suite used for testing is updated ( in TestRobotAppSuite), then the expectations for testing
# below need to be reviewed / updated as well.
############################################
TEST_ROBOT_APP_DIR = SEP.join(HERE.split(SEP)[:-1]) + SEP + 'TestRobotAppSuite'
TEST_SUITE_EXPECTATIONS = {
    'TestRobotAppSuite': {
        'Short Name': 'TestRobotAppSuite',
        'Doc': '',
        'Has Parent': False,
        'Parent': None,
        'Children': ['RobotAppSubDirectory', 'AppSubSuite1', 'AppSubSuite2'],
        'Location': TEST_ROBOT_APP_DIR,
        'Tests': {}
    },
    'TestRobotAppSuite.RobotAppSubDirectory': {
        'Short Name': 'RobotAppSubDirectory',
        'Doc': '',
        'Has Parent': True,
        'Parent': 'TestRobotAppSuite',
        'Children': ['NestedChildSuite', 'TemplateSubSuite', 'AnotherTemplateTestSuite'],
        'Location': TEST_ROBOT_APP_DIR + '\\RobotAppSubDirectory',
        'Tests': {}
    },
    'TestRobotAppSuite.AppSubSuite1': {
        'Short Name': 'AppSubSuite1',
        'Doc': 'A test suite with a single test for valid login.\\n\\n'
               'This test has a workflow that is created using keywords in\\n'
               'the imported resource file.',
        'Has Parent': True,
        'Parent': 'TestRobotAppSuite',
        'Children': [],
        'Location': TEST_ROBOT_APP_DIR + '\\AppSubSuite1.robot',
        'Tests': {
            'Valid Login': {
                'Doc': '',
                'Steps': []
            }
        }
    },
    'TestRobotAppSuite.AppSubSuite2': {
        'Short Name': 'AppSubSuite2',
        'Doc': 'Example using the space separated plain text format.',
        'Has Parent': True,
        'Parent': 'TestRobotAppSuite',
        'Children': [],
        'Location': TEST_ROBOT_APP_DIR + '\\AppSubSuite2.txt',
        'Tests': {
            'My Test': {
                'Doc': 'Example test',
                'Steps': []
            },
            'Another Test': {
                'Doc': '',
                'Steps': []
            },
        }
    },
    'TestRobotAppSuite.RobotAppSubDirectory.NestedChildSuite': {
        'Short Name': 'NestedChildSuite',
        'Doc': '',
        'Has Parent': True,
        'Children': ['NestedTestSuite_GivenWhenThen'],
        'Parent': 'RobotAppSubDirectory',
        'Location': TEST_ROBOT_APP_DIR + '\\RobotAppSubDirectory\\NestedChildSuite',
        'Tests': {}
    },
    'TestRobotAppSuite.RobotAppSubDirectory.TemplateSubSuite': {
        'Short Name': 'TemplateSubSuite',
        'Doc': '',
        'Has Parent': True,
        'Parent': 'RobotAppSubDirectory',
        'Children': [],
        'Location': TEST_ROBOT_APP_DIR + '\\RobotAppSubDirectory\\TemplateSubSuite.robot',
        'Tests': {
            'Invalid Username': {
                'Doc': '',
                'Steps': []
            },
            'Invalid Password': {
                'Doc': '',
                'Steps': []
            },
            'Invalid Username And Password': {
                'Doc': '',
                'Steps': []
            },
            'Empty Username': {
                'Doc': '',
                'Steps': []
            },
            'Empty Password': {
                'Doc': '',
                'Steps': []
            },
            'Empty Username And Password': {
                'Doc': '',
                'Steps': []
            },
        }
    },
    'TestRobotAppSuite.RobotAppSubDirectory.AnotherTemplateTestSuite': {
        'Short Name': 'AnotherTemplateTestSuite',
        'Doc': '',
        'Has Parent': True,
        'Parent': 'RobotAppSubDirectory',
        'Children': [],
        'Location': TEST_ROBOT_APP_DIR + '\\RobotAppSubDirectory\\AnotherTemplateTestSuite.robot',
        'Tests': {
            'Additions': {
                'Doc': '',
                'Steps': []
            },
            'Substractions': {
                'Doc': '',
                'Steps': []
            },
            'Multiplication': {
                'Doc': '',
                'Steps': []
            },
            'Division': {
                'Doc': '',
                'Steps': []
            },
            'Calculation error': {
                'Doc': '',
                'Steps': ''
            }
        }
    },
    'TestRobotAppSuite.RobotAppSubDirectory.NestedChildSuite.NestedTestSuite GivenWhenThen': {
        'Short Name': 'AnotherTemplateTestSuite',
        'Doc': '',
        'Has Parent': True,
        'Parent': 'NestedChildSuite',
        'Location': UTEST_ROOT + '\\TestRobotAppSuite\\RobotAppSubDirectory\\NestedChildSuite\\'
                                 'NestedTestSuite_GivenWhenThen.robot',
        'Tests': {
            'Addition': {
                'Doc': '',
                'Steps': []
            }
        }
    },
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
                                                                     app_test_location='')  # This is the bad part.

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
        self.assertEqual(len(discovered_app.test_suites), len(TEST_SUITE_EXPECTATIONS))
        for s in discovered_app.test_suites:
            self.assertIsNotNone(TEST_SUITE_EXPECTATIONS.get(s.name),
                                 msg='Unexpected test suite discovered.')
            self.assertEqual(TEST_SUITE_EXPECTATIONS.get(s.name)['Location'],
                             s.location,
                             msg='Unexpected test suite location discovered.')
            self.assertEqual(TEST_SUITE_EXPECTATIONS.get(s.name)['Doc'],
                             s.documentation,
                             msg='Unexpected test suite documentation')
            if TEST_SUITE_EXPECTATIONS.get(s.name)['Has Parent']:
                self.assertEqual(TEST_SUITE_EXPECTATIONS.get(s.name)['Parent'], s.name.split('.')[-2])
            else:
                self.assertEqual(len(s.name.split('.')), 1)

    def test_robot_test_discovery(self):
        discovered_app = DiscoveredRobotApplication(self.test_robot_app)
        discovered_app.discover_suites_and_tests()
        for s in discovered_app.test_suites:
            expected_tests = TEST_SUITE_EXPECTATIONS.get(s.name)['Tests']
            self.assertEqual(len(expected_tests), len(s.tests),
                             msg='Unexpected tests discovered in suite: ' + s.name)
            for t in s.tests:   # DiscoveredRobotTest
                self.assertIsInstance(t, DiscoveredRobotTest)
                self.assertIsNotNone(expected_tests.get(t.name),
                                     msg='Unexpected test found in {s}: {t}'.format(s=s.name, t=t.name))
                self.assertEqual(expected_tests.get(t.name)['Doc'],
                                 t.documentation,
                                 msg='Discovered test documentation for {t} incorrect: {d}'.format(t=t.name,
                                                                                                   d=t.documentation))

    def test_child_test_suite_discovery_only(self):
        discovered_app = DiscoveredRobotApplication(self.test_robot_app)
        discovered_app.discover_suites_and_tests()
        discovered_app.configure_suites_and_tests()     # Configure this to create saved RobotTestSuite in test DB
        existing_robot_suite = RobotTestSuite.objects.get(name='RobotAppSubDirectory')
        discovered_suite = DiscoveredRobotTestSuite(robot_suite=existing_robot_suite)
        discovered_suite.discover_child_suites_and_tests()
        self.assertIsNotNone(TEST_SUITE_EXPECTATIONS.get(discovered_suite.name),
                             msg='Discovered child suite had an unexpected name: ' + discovered_suite.name)
        self.assertEqual(len(TEST_SUITE_EXPECTATIONS.get(discovered_suite.name)['Children']),
                         len(discovered_suite.child_suites),
                         msg='Unexpected number of child suites discovered in: ' + discovered_suite.name)
        for child in discovered_suite.child_suites:
            child_short_name = child.name.split(existing_robot_suite.name + '.')[-1]
            self.assertEquals(TEST_SUITE_EXPECTATIONS.get(discovered_suite.name)['Children'].count(child_short_name), 1,
                              msg=child_short_name)

    def test_remove_suite_from_app(self):
        pass

    def test_remove_child_suite_from_parent_and_app(self):
        pass

    def test_remove_test_from_suite(self):
        pass


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

    def test_configure_robot_suite(self):
        pass

    def test_configure_robot_test(self):
        pass

    def test_do_not_create_duplicate_root_suites(self):
        pass
