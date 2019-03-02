Robot Web Project
=================

A Django project built to support developing, running, and reporting on Robot Framework tests.

Environment Variables
---------------------

The following environment variable should be set on the machine hosting the robotweb site:

    - **ROBOT_PROJECT_PATH**: The path to the parent directory that contains the Robot Framework tests on this machine.
                              This is used to narrow down the search space for robot tests and configuring information
                              about applications under test.

Run Django tests cases with full verbosity
------------------------------------------
Django supports a wide range of testing by extending Python's built-in `unittest.TestCase`. Execute the tests for this
project by running the following command from the project's root directory (make sure your virtual env is activated).::

    > python -Wa manage.py test --verbosity=2
