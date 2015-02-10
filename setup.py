#!/usr/bin/env python

from __future__ import print_function
from setuptools import setup
from setuptools import find_packages
from setuptools.command.test import test as TestCommand
import io
import os
import sys


here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


about={}
initfile = os.path.join(here, 'src', 'easymodel', '__init__.py')
with open(initfile) as fp:
    exec(fp.read(), about)

long_description = read('README.rst', 'HISTORY.rst')
install_requires = ['PySide']
tests_require = ['pytest']


setup(
    name='easymodel',
    version=about['__version__'],
    description='Qt Models and Views made easy with general purpose Model and a Widget delegate.',
    long_description=long_description,
    author=about['__author__'],
    author_email=about['__email__'],
    url='https://github.com/storax/easymodel',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    tests_require=tests_require,
    install_requires=install_requires,
    cmdclass={'test': PyTest},
    license='BSD',
    zip_safe=False,
    keywords='easymodel',
    test_suite='easymodel.test.easymodel',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
)
