from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='IrssiReader',
    version=version,
    description="Pipes irssi logs to festival",
    long_description="""\
    """,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Nick Murdoch',
    author_email='nick@nivan.net',
    url='http://nickmurdoch.nivan.net',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      # -*- Extra requirements: -*-
    ],
    entry_points={
        'console_scripts': [
            'read-irssi = irssireader:main',
        ],
    },
)
