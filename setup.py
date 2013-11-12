# Copyright (c) Aaron Gallagher <_@habnab.it>
# See COPYING for details.

from setuptools import setup


with open('README.rst', 'rb') as infile:
    long_description = infile.read()

with open('requirements.txt', 'rb') as infile:
    install_requires = infile.read().split()

setup(
    name='launchdcheckin',
    description='launchd checkin for python and twisted',
    long_description=long_description,
    author='Aaron Gallagher',
    author_email='_@habnab.it',
    url='https://github.com/habnabit/launchdcheckin',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
    ],
    license='ISC',

    setup_requires=['vcversioner>=1'],
    vcversioner={
        'version_module_paths': ['launchdcheckin/_version.py'],
    },
    install_requires=install_requires,
    packages=['launchdcheckin', 'twisted.plugins'],
)

# Make Twisted regenerate the dropin.cache, if possible.  This is necessary
# because in a site-wide install, dropin.cache cannot be rewritten by
# normal users.
try:
    from twisted.plugin import IPlugin, getPlugins
except ImportError:
    pass
else:
    list(getPlugins(IPlugin))
