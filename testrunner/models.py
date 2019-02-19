from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
# from django.contrib.auth.models import User
# Create your models here.


class BaseObject(models.Model):
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True,
                                   editable=False,
                                   help_text='Designates when this thing was created.')
    modified = models.DateTimeField(auto_now=True,
                                    help_text='Designates when this thing was last modified.')
    # created_by = models.ForeignKey(User,
    #                                on_delete=models.PROTECT,
    #                                help_text='Designates who created this thing.',
    #                                related_name='record_creator')
    # modified_by = models.ForeignKey(User,
    #                                 on_delete=models.PROTECT,
    #                                 help_text='Designates who last changed this thing.',
    #                                 related_name='record_modifier')

    def __str__(self):
        return self.name


class RobotTestSuite(BaseObject):
    documentation = models.TextField(max_length=4000, null=True)
    parent = models.ForeignKey('self',
                               on_delete=models.CASCADE,
                               null=True,
                               related_name='child_suite',
                               related_query_name='parent_suite')


class RobotTest(BaseObject):
    documentation = models.TextField(max_length=4000, null=True)
    robot_suite = models.ForeignKey(RobotTestSuite,
                                    on_delete=models.CASCADE,
                                    null=True,
                                    related_name='test',
                                    related_query_name='suite')


class RobotTestStep(BaseObject):
    keyword = models.CharField(max_length=200)
    robot_test = models.ForeignKey(RobotTest,
                                   on_delete=models.CASCADE)
    order = models.IntegerField('execution order',
                                validators=[MinValueValidator(0)])
    arguments = models.TextField(max_length=4000,
                                 help_text='A pipe separated string of arguments passed to the test step keyword.',
                                 null=True)


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
        return '{name}: {result}'.format(name=self.test.name, result=self.result)

    def set_execution_time(self):
        self.execution_time = self.end_time - self.start_time
