from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='robotweb',
    version='0.0.1',
    url='',
    author='Michael Rose',
    author_email='michael.rose@theice.com',
    classifiers=[
        'Development Status :: 4 - Beta',
    ],
    long_description=long_description,
    packages=find_packages('src', exclude=['contrib', 'docs', 'atest', 'utest']),
    python_requires='>=3.5',
    install_requires=['django>=2.1.7', 'robotframework>=3.1.1'],
    description='A web utility for executing Robot Framework tests and viewing test results from a browser.'
)