import logging
import subprocess

from .exceptions import RobotExecutionException

logger = logging.getLogger(__name__)


class RobotExecutionEngine:

    SUPPORTED_ROBOTWEB_OPTIONS = ['loglevel', 'dryrun', 'output', 'outputdir', 'include', 'exclude']

    def __init__(self, tests=None, suites=None, application=None, **options):
        """
        Use this object to execute Robot Framework tests with the specified robot ``executable``.  Optionally
        provide the names of desired tests and test suites to run, as well as the location of those tests
        on the local machine. Accepted keyword arguments are listed below. In order to allow running tests with
        a dynamic robot executable (and related libraries), this object invokes Python's built-in subprocess module.
        :param tests: a list of testrunner.models.RobotTest
        :param suites: a list of testrunner.models.RobotTestSuite
        :param application: the testrunner.models.RobotApplicationUnderTest to run tests for.
        :param options: Optional keyword arguments to run robot with:
        ``loglevel``  - TRACE,DEBUG, INFO (default), WARN, NONE (no logging)
        ``dryrun``    - True, False (default)
        ``output``    - Name of the output file or NONE. Default is output.xml for RF, but will be NONE for the purposes
                       of this application, as output will instead be displayed to the user in the web page.
        ``outputdir`` - The location to save the output files created by Robot Framework
        ``include``   - Include tests with this tag pattern when running robot
        ``exclude``   - Exclude tests with this tag pattern when running robot

        Tags and patterns can be combined together with `AND`, `OR`, and `NOT` operators, and using pattern * and ?.
                Examples: --include foo --include bar*
                --include fooANDbar*

        """
        self.application = application
        self.suites = suites
        self.tests = tests
        if application is not None:
            logger.info('Setting executable and test location based on input application: ' + str(application))
            self.executable = application.robot_location
            self.tests_location = application.app_test_location
        elif application is None and suites is not None:
            logger.info('Attempting to set executable and test location based on input test suites.')
            if len(set([s.application.robot_location for s in suites])) != 1:
                raise RobotExecutionException('Tried to configure the execution engine with tests from different '
                                              'applications or an empty iterable was provided to the engine. This is '
                                              'not allowed. Make sure that all tests / test suites are associated with '
                                              'one application per test run and that test objects are not empty.')
            self.executable = suites[0].application.robot_location
            self.tests_location = suites[0].application.app_test_location
        elif application is None and suites is None and tests is not None:
            logger.info('Attempting to set executable and test location based on input tests.')
            if len(set([t.robot_suite.application.robot_location for t in tests])) != 1:
                raise RobotExecutionException('Tried to configure the execution engine with tests from different '
                                              'applications or an empty iterable was provided to the engine. This is '
                                              'not allowed. Make sure that all tests / test suites are associated with '
                                              'one application per test run and that test objects are not empty.')
            self.executable = tests[0].robot_suite.application.robot_location
            self.tests_location = tests[0].robot_suite.application.app_test_location
        else:
            raise RobotExecutionException('Invalid usage of Robot Execution Engine: a list of tests, suites, or an '
                                          'application for testing must be provided at minimum.')
        self._command = list()
        self.execution_result = None
        self.robot_output = None
        # Default optional kw args
        self.loglevel = self.output = self.outputdir = self.include = self.exclude = self.dryrun = None
        if not all([(option in self.SUPPORTED_ROBOTWEB_OPTIONS) for option in options]):
            raise RobotExecutionException('Unsupported options passed to RobotWeb test execution engine.')
        else:
            for option, value in options.items():
                setattr(self, option, value)

    def _add_to_command(self, *args):
        """Add specified arguments to the list of command line arguments. The executable location must be set first."""
        if not self._command and self.executable is None:
            raise RobotExecutionException('Cannot add command line arguments before the robot executable is set.')
        elif not self._command and self.executable is not None:
            self._command.append(self.executable)
            self._command.extend(args)
        else:
            self._command.extend(args)

    def _validate_robot_executable(self):
        if not (self.executable.endswith('robot') or self.executable.endswith('robot.exe')):
            raise RobotExecutionException('The robot executable was not defined correctly for this application. Please '
                                          'check that and try again.')

    def _run_with_tags(self, tag_type, tag_text):
        if tag_type.lower() == 'include':
            self._add_to_command('--include', tag_text)
        elif tag_type.lower() == 'exclude':
            self._add_to_command('--exclude', tag_text)
        else:
            pass

    def _handle_options(self):
        if self.include is not None:
            self._run_with_tags('include', self.include)
        if self.exclude is not None:
            self._run_with_tags('exclude', self.exclude)
        if self.loglevel is not None:
            self._add_to_command('--loglevel', self.loglevel)
        if self.dryrun is not None and self.dryrun:
            self._add_to_command('--dryrun')

    def _handle_output(self):
        if self.output is not None:
            self._add_to_command('--output', self.output)
        elif self.outputdir is not None and self.output is None:
            self._add_to_command('--outputdir', self.outputdir)
        elif self.outputdir is not None and self.output is not None:
            self._add_to_command('--outputdir', self.outputdir)
        else:
            self._add_to_command('--outputdir', 'output')

    def _handle_tests(self):
        if self.tests:
            for test in self.tests:
                self._add_to_command('--test', test.name)
        if self.suites:
            for suite in self.suites:
                self._add_to_command('--suite', suite.name)
        if self.application is not None:
            self._add_to_command(self.application.app_test_location)
        elif self.suites is not None:
            self._add_to_command(self.suites[0].application.app_test_location)
        else:
            self._add_to_command(self.tests[0].robot_suite.application.app_test_location)

    def run_subprocess(self):
        self._validate_robot_executable()
        self._handle_options()
        self._handle_output()
        self._handle_tests()
        logger.info('About to send the following command to subprocess: ' + str(self._command))
        completed_process = subprocess.run(self._command,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
        if completed_process.stderr:
            logger.error('There were some errors when executing the tests: ')
            for l in completed_process.stderr.decode('utf-8').split('\n'):
                logger.error(l)
        self.robot_output = completed_process.stdout.decode('utf-8')
        for l in self.robot_output.split('\n'):
            logger.info(l)
        self._command = list()  # to allow for reruns if desired
