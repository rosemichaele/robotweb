import os
from django.test import TestCase, TransactionTestCase
from robot.parsing.model import TestDataDirectory

from testrunner.models import RobotApplicationUnderTest, RobotTestSuite, RobotTest
from robotapi.discover import DiscoveredRobotTest, DiscoveredRobotTestSuite, DiscoveredRobotApplication
from robotapi.exceptions import RobotDiscoveryException, RobotExecutionException
from robotapi.execute import RobotExecutionEngine

from robotweb.settings import BASE_DIR

SEP = os.path.sep
HERE = os.path.realpath(__file__)
UTEST_ROOT = SEP.join(HERE.split(SEP)[:-1])
###########################################
# If the example test suite used for testing is updated (in TestRobotAppSuite), then the expectations for testing
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
        'Location': TEST_ROBOT_APP_DIR + SEP + 'RobotAppSubDirectory',
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
        'Location': TEST_ROBOT_APP_DIR + SEP + 'AppSubSuite1.robot',
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
        'Location': TEST_ROBOT_APP_DIR + SEP + 'AppSubSuite2.robot',
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
        'Location': TEST_ROBOT_APP_DIR + SEP.join(['', 'RobotAppSubDirectory','NestedChildSuite']),
        'Tests': {},
    },
    'TestRobotAppSuite.RobotAppSubDirectory.TemplateSubSuite': {
        'Short Name': 'TemplateSubSuite',
        'Doc': '',
        'Has Parent': True,
        'Parent': 'RobotAppSubDirectory',
        'Children': [],
        'Location': TEST_ROBOT_APP_DIR + SEP.join(['', 'RobotAppSubDirectory', 'TemplateSubSuite.robot']),
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
        'Location': TEST_ROBOT_APP_DIR + SEP.join(['', 'RobotAppSubDirectory', 'AnotherTemplateTestSuite.robot']),
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
        'Short Name': 'NestedTestSuite GivenWhenThen',
        'Doc': '',
        'Has Parent': True,
        'Parent': 'NestedChildSuite',
        'Location': UTEST_ROOT + SEP.join(['', 'TestRobotAppSuite', 'RobotAppSubDirectory', 'NestedChildSuite',
                                           'NestedTestSuite_GivenWhenThen.robot']),
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
        print('\nRunning robotapi discovery unit tests in: ' + HERE)
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
        self.assertEqual(repr(discovered_app), 'DiscoveredRobotApplication: ' + 'My Test Robot App')

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
            self.assertEqual(TEST_SUITE_EXPECTATIONS.get(discovered_suite.name)['Children'].count(child_short_name), 1,
                             msg=child_short_name)

    def test_remove_suite_from_app(self):
        discovered_app = DiscoveredRobotApplication(self.test_robot_app)
        discovered_app.discover_suites_and_tests()
        remove_suite = 'TestRobotAppSuite.RobotAppSubDirectory.NestedChildSuite'
        discovered_app.remove_discovered_test_suite(remove_suite)
        self.assertEqual(len([e for e in TEST_SUITE_EXPECTATIONS if not e.startswith(remove_suite)]),
                         len(discovered_app.test_suites),
                         msg='Test suite removal from discovered app was not successful.')
        self.assertNotIn(remove_suite, discovered_app.test_suites,
                         msg='Test suite was not removed from the app.')

    def test_remove_child_suite_from_parent_and_app(self):
        discovered_app = DiscoveredRobotApplication(self.test_robot_app)
        discovered_app.discover_suites_and_tests()
        parent = 'TestRobotAppSuite.RobotAppSubDirectory'
        discovered_suite = [ds for ds in discovered_app.test_suites
                            if ds.name == parent][0]
        remove_child_suite = 'TestRobotAppSuite.RobotAppSubDirectory.TemplateSubSuite'
        discovered_suite.remove_discovered_child_suite(remove_child_suite)
        self.assertEqual(len(discovered_suite.child_suites),
                         len([e for e in TEST_SUITE_EXPECTATIONS.get(parent)['Children']
                              if e != TEST_SUITE_EXPECTATIONS.get(remove_child_suite)['Short Name']]),
                         msg='Child test suite removal was not successful.')
        self.assertNotIn(remove_child_suite,
                         discovered_suite.child_suites,
                         msg='Child test suite was not removed from the its parent.')
        self.assertEqual(len([e for e in TEST_SUITE_EXPECTATIONS if not e.startswith(remove_child_suite)]),
                         len(discovered_app.test_suites),
                         msg='Child test suite removal from discovered app was not successful.')
        self.assertNotIn(remove_child_suite,
                         discovered_app.test_suites,
                         msg='Child test suite was not removed from the disocvered app.')

    def test_remove_test_from_suite(self):
        discovered_app = DiscoveredRobotApplication(self.test_robot_app)
        discovered_app.discover_suites_and_tests()
        test_suite = 'TestRobotAppSuite.AppSubSuite2'
        discovered_suite = [ds for ds in discovered_app.test_suites
                            if ds.name == test_suite][0]
        remove_test = 'Another Test'
        discovered_suite.remove_discovered_test(remove_test)
        self.assertEqual(len([t for t in TEST_SUITE_EXPECTATIONS.get(test_suite)['Tests'] if t != remove_test]),
                         len(discovered_suite.tests),
                         msg='Test removal from test suite was unsuccessful.')
        self.assertNotIn(remove_test,
                         discovered_suite.tests,
                         msg='Test was not removed from the discovered suite.')


class TestConfiguration(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        print('\nRunning robotapi configuration unit tests in: ' + HERE)
        print('Dummy Robot test suite located here: ' + TEST_ROBOT_APP_DIR)
        # Create a dummy RobotApplicationUnderTest object saved in the test database (in memory for SQLite3)

    def setUp(self):
        self.test_robot_app = RobotApplicationUnderTest.objects.create(name='My Test Robot App',
                                                                       description='An application created for testing '
                                                                                   'RobotWeb discovery tools.',
                                                                       robot_location=HERE,
                                                                       app_test_location=TEST_ROBOT_APP_DIR)

    def test_suites_must_be_discovered_before_configured(self):
        discovered_app_suites_not_discovered = DiscoveredRobotApplication(self.test_robot_app)
        with self.assertRaisesMessage(RobotDiscoveryException, 'Tests and suites must be discovered before '
                                                               'they can be configured.'):
            discovered_app_suites_not_discovered.configure_suites_and_tests()

    def test_configure_robot_suite_before_parent_raises(self):
        discovered_app = DiscoveredRobotApplication(self.test_robot_app)
        discovered_app.discover_suites_and_tests()
        parent_verbose = 'TestRobotAppSuite.RobotAppSubDirectory'
        suite_name = 'TestRobotAppSuite.RobotAppSubDirectory.TemplateSubSuite'
        suite_to_configure = [s for s in discovered_app.test_suites if s.name == suite_name][0]
        with self.assertRaisesMessage(RobotDiscoveryException, 'There should have been an existing parent suite, but '
                                                               'one was not found. Tried to find a test suite with '
                                                               'this verbose/display name: ' + parent_verbose):
            suite_to_configure.configure()

    def test_configure_robot_test_before_suite_raises(self):
        discovered_app = DiscoveredRobotApplication(self.test_robot_app)
        discovered_app.discover_suites_and_tests()
        suite_verbose = 'TestRobotAppSuite.RobotAppSubDirectory.TemplateSubSuite'
        test_name = 'Invalid Username And Password'
        suite_to_configure = [s for s in discovered_app.test_suites if s.name == suite_verbose][0]
        test_to_configure = [t for t in suite_to_configure.tests if t.name == test_name][0]
        with self.assertRaisesMessage(RobotDiscoveryException, 'There should have been an existing test suite for '
                                                               'this test, but one was not found: ' + suite_verbose):
            test_to_configure.configure()

    def test_prevent_duplicate_root_suites(self):
        discovered_app = DiscoveredRobotApplication(self.test_robot_app)
        discovered_app.discover_suites_and_tests()
        discovered_app.root_suite.configure()
        discovered_app.root_suite.configure()  # prevent root suite dupes, parent == NULL
        self.assertEqual(len(RobotTestSuite.objects.filter(name='TestRobotAppSuite')), 1)

    def test_configure_robot_app(self):
        discovered_app = DiscoveredRobotApplication(self.test_robot_app)
        discovered_app.discover_suites_and_tests()
        discovered_app.configure_suites_and_tests()
        all_suites = RobotTestSuite.objects.all()
        self.assertEqual(len(all_suites), len(TEST_SUITE_EXPECTATIONS))
        for suite in all_suites:
            expected_suite_info = TEST_SUITE_EXPECTATIONS.get(suite.verbose_name)
            self.assertEqual(expected_suite_info['Short Name'], suite.name)
            self.assertEqual(expected_suite_info['Doc'], suite.documentation)
            self.assertEqual(suite.application, self.test_robot_app)
            self.assertEqual(expected_suite_info['Location'], suite.suite_location)
            if expected_suite_info['Parent'] is not None:
                self.assertEqual(expected_suite_info['Parent'], suite.parent.name)
            all_suite_tests = RobotTest.objects.filter(robot_suite=suite)
            self.assertEqual(len(all_suite_tests), len(expected_suite_info['Tests']))
            for test in all_suite_tests:
                test_info = expected_suite_info.get('Tests')
                self.assertIsInstance(test, RobotTest)
                self.assertIsNotNone(test_info.get(test.name))
                self.assertEqual(test.documentation, test_info.get(test.name)['Doc'])


class TestExecution(TestCase):
    @classmethod
    def setUpTestData(cls):
        print('\nRunning robotapi test execution unit tests in: ' + HERE)
        print('Dummy Robot test suite located here: ' + TEST_ROBOT_APP_DIR)
        # Create a dummy RobotApplicationUnderTest object saved in the test database (in memory for SQLite3)
        cls.test_robot_app = RobotApplicationUnderTest.objects.create(name='My Test Robot App',
                                                                      description='An application created for testing '
                                                                                  'RobotWeb discovery tools.',
                                                                      robot_location=BASE_DIR,
                                                                      app_test_location=TEST_ROBOT_APP_DIR)
        discovered_app = DiscoveredRobotApplication(cls.test_robot_app)
        discovered_app.discover_suites_and_tests()
        discovered_app.configure_suites_and_tests()
        cls.other_robot_app = RobotApplicationUnderTest.objects.create(name='My Other Test Robot App',
                                                                       description='Another application created for '
                                                                                   'testing RobotWeb discovery tools.',
                                                                       robot_location=os.getenv('ROBOT_PROJECT_PATH') +
                                                                                                 SEP.join(['', 'path',
                                                                                                           'to', 'other',
                                                                                                           'robot']),
                                                                       app_test_location=os.getenv('ROBOT_PROJECT_PATH')
                                                                                                   + SEP.join(['',
                                                                                                               'path',
                                                                                                               'to',
                                                                                                               'other',
                                                                                                               'tests'])
                                                                       )

    @staticmethod
    def set_robot_for_app(app: RobotApplicationUnderTest, robot_location: str):
        app.robot_location = robot_location
        app.save()

    def test_execute_with_correct_robot(self):
        app = self.other_robot_app
        robot = RobotExecutionEngine(application=app)
        self.assertEqual(self.other_robot_app.robot_location,
                         robot.executable,
                         msg='RobotExecutionEngine did not set the executable attribute correctly.')

    def test_executable_is_robot(self):
        app = self.test_robot_app
        with self.assertRaisesMessage(RobotExecutionException, 'The robot executable was not defined correctly for this'
                                                               ' application. Please check that and try again.'):
            robot = RobotExecutionEngine(application=app)
            robot.run_subprocess()

    def test_cannot_test_multiple_apps_at_once(self):
        suites = RobotTestSuite.objects.all()
        suite_different_app = suites[0]
        suite_different_app.application = self.other_robot_app
        suite_different_app.save()
        with self.assertRaisesMessage(RobotExecutionException, 'Tried to configure the execution engine with tests '
                                                               'from different applications. This is not allowed. Make '
                                                               'sure that all tests / test suites are associated with '
                                                               'one application per test run.'):
            robot = RobotExecutionEngine(suites=suites)
            robot.run_subprocess()

    def test_unsupported_options_passed_to_engine(self):
        with self.assertRaisesMessage(RobotExecutionException, 'Unsupported options passed to RobotWeb test execution '
                                                               'engine.'):
            RobotExecutionEngine(application=self.test_robot_app,
                                 michael='cool')

    def test_execute_robot_test(self):
        self.set_robot_for_app(self.test_robot_app, 'robot')
        tests = [RobotTest.objects.all()[0]]
        robot = RobotExecutionEngine(tests=tests)
        robot.run_subprocess()
        self.assertIsNotNone(robot.robot_output,
                             msg='Robot did not execute the test as expected.')
        self.assertIn(tests[0].name,
                      robot.robot_output,
                      msg='Test result did not contain the expected test name.')
        self.addCleanup(self.set_robot_for_app, self.test_robot_app, HERE)

    def test_execute_robot_suite(self):
        self.set_robot_for_app(self.test_robot_app, 'robot')
        suites = [RobotTestSuite.objects.all()[0]]
        robot = RobotExecutionEngine(suites=suites)
        robot.run_subprocess()
        self.assertIsNotNone(robot.robot_output,
                             msg='Robot did not execute the suite as expected.')
        self.assertIn(suites[0].name,
                      robot.robot_output,
                      msg='Test result did not contains the expected suite name.')
        self.addCleanup(self.set_robot_for_app, self.test_robot_app, HERE)

    def test_execute_robot_with_tags(self):
        include_tags = 'smokeORregression'
        exclude_tags = 'auth*'
        robot = RobotExecutionEngine(application=self.test_robot_app,
                                     include=include_tags,
                                     exclude=exclude_tags)
        self.assertEqual(robot.include,
                         include_tags,
                         msg='Include tags were not set correctly.')
        self.assertEqual(robot.exclude,
                         exclude_tags,
                         msg='Exclude tags were not set correctly.')

    def test_execute_output_none_by_default(self):
        robot = RobotExecutionEngine(application=self.test_robot_app)
        self.assertIsNone(robot.output,
                          msg='Execution output should be None by default, but was not.')

    def test_execute_robot_dryrun(self):
        robot = RobotExecutionEngine(application=self.test_robot_app,
                                     dryrun=True)
        self.assertTrue(robot.dryrun)

    def test_execute_robot_with_loglevel(self):
        robot = RobotExecutionEngine(application=self.test_robot_app,
                                     loglevel='DEBUG')
        self.assertEqual(robot.loglevel,
                         'DEBUG',
                         msg='Robot execution engine did not set the desired log level correctly.')

    def test_cannot_execute_without_tests_suites_application(self):
        with self.assertRaisesMessage(RobotExecutionException, 'Invalid usage of Robot Execution Engine: a list of '
                                                               'tests, suites, or an application for testing must be '
                                                               'provided at minimum.'):
            RobotExecutionEngine()

