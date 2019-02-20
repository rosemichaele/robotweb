from django.contrib import admin

from .models import RobotApplicationUnderTest, RobotTestSuite, RobotTest, RobotTestStep, RobotTag, RobotVariable

admin.site.register(RobotApplicationUnderTest)
admin.site.register(RobotTestSuite)
admin.site.register(RobotTest)
admin.site.register(RobotTestStep)
admin.site.register(RobotTag)
admin.site.register(RobotVariable)
