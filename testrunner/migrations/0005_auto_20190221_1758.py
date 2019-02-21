# Generated by Django 2.1.7 on 2019-02-21 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testrunner', '0004_auto_20190220_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robottest',
            name='robot_tags',
            field=models.ManyToManyField(blank=True, to='testrunner.RobotTag'),
        ),
        migrations.AlterField(
            model_name='robotteststep',
            name='arguments',
            field=models.TextField(help_text='A list of arguments passed to the test step keyword with a line break between each.', max_length=4000, null=True),
        ),
        migrations.AlterField(
            model_name='robottestsuite',
            name='robot_tags',
            field=models.ManyToManyField(blank=True, to='testrunner.RobotTag'),
        ),
    ]
