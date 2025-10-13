import os, sys, re

from purdy import __version__

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(readme).read()


SETUP_ARGS = dict(
    name='purdy',
    version=__version__,
    description=('Terminal based code snippet display tool '),
    long_description=long_description,
    url='https://github.com/cltrudeau/purdy',
    author='Christopher Trudeau',
    author_email='ctrudeau+pypi@arsensa.com',
    license='MIT',
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='code display',
    py_modules = ['purdy',],
    scripts=['bin/purdy', 'bin/subpurdy', 'bin/pat', 'bin/prat'],
    install_requires = [
        'asttokens>=2.0.4',
        'Pygments>=2.19.0',
        'urwid>=2.0.1',
        'colored>=1.4.2,<2',
    ],
    tests_require = [
        'waelstow>=0.10.2',
    ]
)

if __name__ == '__main__':
    from setuptools import setup, find_packages

    SETUP_ARGS['packages'] = find_packages()
    setup(**SETUP_ARGS)
