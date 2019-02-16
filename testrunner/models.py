from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

# Create your models here.


class BaseObject(models.Model):
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True)


class TestSuite(BaseObject):
    documentation = models.TextField(max_length=4000, null=True)
    test_count = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

    def set_test_count(self):
        self.test_count = self.tests.count()
        self.modified = timezone.now()
        self.save()


class Test(BaseObject):
    documentation = models.TextField(max_length=4000, null=True)
    suite = models.ForeignKey(TestSuite,
                              on_delete=models.SET_NULL,
                              null=True,
                              related_name="tests",
                              related_query_name="suite")

    def __str__(self):
        return self.name


class TestRun(models.Model):
    test = models.ForeignKey(Test, on_delete=models.PROTECT)
    RESULTS = (
        ("pass", "PASS"),
        ("fail", "FAIL"),
        ("error", "ERROR")
    )
    result = models.CharField(max_length=5, choices=RESULTS)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    execution_time = models.TimeField()
    STATUS_CHOICES = (
        ("not started", "Not Started"),
        ("in progress", "In Progress"),
        ("complete", "Complete"),
        ("error", "Error"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reason = models.TextField(max_length=400, blank=True)

    def __str__(self):
        return "{name}: {result}".format(name=self.test.name, result=self.result)

    def set_execution_time(self):
        self.execution_time = self.end_time - self.start_time
