# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='demiurge',
    version='0.2',
    description='Scraping micro-framework based on pyquery.',
    author='Matias Bordese',
    author_email='mbordese@gmail.com',
    url='https://github.com/matiasb/demiurge',
    packages=[
        'demiurge',
    ],
    package_dir={'demiurge': 'demiurge'},
    include_package_data=True,
    install_requires=[
        'pyquery >= 1.2.8',
    ],
    license="BSD",
    zip_safe=False,
    keywords='scraping pyquery framework scraper web data extraction',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta'
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
)
