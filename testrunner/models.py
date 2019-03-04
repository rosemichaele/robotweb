import os

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
# from django.contrib.auth.models import User


ROBOT_PROJECT_LOCATION = os.environ.get('ROBOT_PROJECT_PATH')
if ROBOT_PROJECT_LOCATION is None:
    raise AssertionError('The ROBOT_PROJECT_PATH environment variable must be set to continue.')


class BaseObject(models.Model):
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True,
                                   editable=False,
                                   help_text='Designates when this thing was created.')
    modified = models.DateTimeField(auto_now=True,
                                    help_text='Designates when this thing was last modified.')

    class Meta:
        abstract = True
    # created_by = models.ForeignKey(User,
    #                                on_delete=models.PROTECT,
    #                                help_text='Designates who created this thing.',
    #                                related_name='records_created')
    # modified_by = models.ForeignKey(User,
    #                                 on_delete=models.PROTECT,
    #                                 help_text='Designates who last changed this thing.',
    #                                 related_name='records_modified')

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class RobotApplicationUnderTest(BaseObject):
    description = models.TextField(max_length=4000,
                                   null=True,
                                   blank=True)
    app_test_location = models.FilePathField(path=ROBOT_PROJECT_LOCATION,
                                             default=ROBOT_PROJECT_LOCATION,
                                             allow_files=False,
                                             allow_folders=True,
                                             max_length=200,
                                             recursive=True,
                                             editable=False,
                                             help_text='The local path to the directory that contains Robot tests for '
                                                       'this app. Defaults to ROBOT_PROJECT_PATH env variable.')
    robot_location = models.CharField(max_length=200,
                                      help_text='Provide the path to the local robot executable to use when running '
                                                ' the tests for this application.')

    class Meta:
        verbose_name = 'Robot application under test'
        verbose_name_plural = 'Robot applications under test'


class RobotTestEnvironment(BaseObject):
    description = models.TextField(max_length=4000,
                                   null=True,
                                   blank=True)
    host_url = models.URLField(verbose_name='Web URL',
                               help_text='The base URL to use for testing this application.')
    for_application = models.ForeignKey(RobotApplicationUnderTest,
                                        verbose_name='Test environment for',
                                        on_delete=models.CASCADE,
                                        related_name='app_test_environment',
                                        related_query_name='for_application')

    class Meta:
        unique_together = ('for_application', 'name')

    def __str__(self):
        return '{app}: {name}'.format(app=self.for_application.name, name=self.name)


class RobotTag(BaseObject):
    application = models.ForeignKey(RobotApplicationUnderTest,
                                    on_delete=models.CASCADE,
                                    related_name='app_robot_tag',
                                    related_query_name='parent_application',
                                    null=True)
    description = models.TextField(max_length=4000, blank=True, null=True)


class RobotVariable(BaseObject):
    application = models.ForeignKey(RobotApplicationUnderTest,
                                    on_delete=models.CASCADE,
                                    related_name='app_robot_variable',
                                    related_query_name='parent_application',
                                    null=True)
    description = models.TextField(max_length=4000, blank=True, null=True)
    value = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return '<{name}:{value}>'.format(name=self.name, value=self.value)


class RobotTestSuite(BaseObject):
    documentation = models.TextField(max_length=4000, null=True)
    application = models.ForeignKey(RobotApplicationUnderTest,
                                    on_delete=models.CASCADE,
                                    related_name='app_suite',
                                    related_query_name='parent_application')
    parent = models.ForeignKey('self',
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True,
                               default='',
                               related_name='child_suite',
                               related_query_name='parent_suite')
    robot_tags = models.ManyToManyField(RobotTag,
                                        blank=True)

    suite_location = models.FilePathField(path=ROBOT_PROJECT_LOCATION,
                                          default=ROBOT_PROJECT_LOCATION,
                                          allow_files=True,
                                          allow_folders=True,
                                          max_length=200,
                                          recursive=True,
                                          editable=False,
                                          help_text='The local path to the directory or file that contains tests for '           
                                                    'this suite. Options to select this will populate after an '
                                                    'application is selected and saved.')

    class Meta:
        unique_together = ('application', 'parent', 'name')

    def __str__(self):
        return '{app}: {name}'.format(app=self.application.name, name=self.verbose_name)

    @property
    def verbose_name(self):
        this_suite = self
        names = [str(self.name)]
        while this_suite.parent:
            names.append(str(this_suite.parent.name))
            this_suite = this_suite.parent
        return '.'.join(list(reversed(names)))


class RobotTest(BaseObject):
    documentation = models.TextField(max_length=4000, null=True)
    robot_suite = models.ForeignKey(RobotTestSuite,
                                    on_delete=models.CASCADE,
                                    related_name='test',
                                    related_query_name='suite')
    robot_tags = models.ManyToManyField(RobotTag,
                                        blank=True)

    class Meta:
        unique_together = ('robot_suite', 'name')

    @property
    def verbose_name(self):
        return self.robot_suite.verbose_name + '.' + self.name

    def __str__(self):
        return '{app}: {name}'.format(app=self.robot_suite.application, name=self.name)


class RobotTestStep(BaseObject):
    keyword = models.CharField(max_length=200)
    robot_test = models.ForeignKey(RobotTest,
                                   on_delete=models.CASCADE)
    order = models.IntegerField('execution order',
                                validators=[MinValueValidator(0)])
    arguments = models.TextField(max_length=4000,
                                 help_text='A list of arguments passed to the test step keyword '
                                           'with a line break between each.',
                                 null=True,
                                 blank=True)


class RobotTestRun(models.Model):
    robot_test = models.ForeignKey(RobotTest, on_delete=models.PROTECT)
    RESULTS = (
        ('pass', 'PASS'),
        ('fail', 'FAIL'),
        ('error', 'ERROR')
    )
    result = models.CharField(max_length=5,
                              choices=RESULTS,
                              help_text='The final result of the test execution.')
    start_time = models.DateTimeField(default=timezone.now,
                                      help_text='When test execution started.')
    end_time = models.DateTimeField(help_text='When test execution ended.')
    execution_time = models.TimeField()
    STATUS_CHOICES = (
        ('not started', 'Not Started'),
        ('in progress', 'In Progress'),
        ('complete', 'Complete'),
        ('error', 'Error'),
    )
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES,
                              help_text='The current status of this test run.')
    reason = models.TextField(max_length=400,
                              blank=True,
                              help_text='Why the test run has the current status.')

    def __str__(self):
        return '{name}: {result} - completed at {end}'.format(name=self.robot_test.name,
                                                              result=self.result,
                                                              end=self.end_time)

    def set_execution_time(self):
        self.execution_time = self.end_time - self.start_time
