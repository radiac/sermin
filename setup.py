import distutils
import os
from setuptools import setup, find_packages
import subprocess


class VagrantCommand(distutils.cmd.Command):
    description = 'Run tests in the active vagrant machine'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        command = [
            'vagrant', 'ssh', '-c', (
                'export SERMIN_TEST_MODE=full && '
                'source $HOME/venv/bin/activate && '
                'cd $HOME/source && '
                'flake8 && '
                'sudo $HOME/venv/bin/python setup.py nosetests -s -vv'
            ),
        ]
        self.announce(
            'Running command: {}'.format(' '.join(command)),
            level=distutils.log.INFO,
        )
        subprocess.call(command)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="sermin",
    version='0.0.1',
    author="Richard Terry",
    author_email="python@radiac.net",
    description=("Framework for system configuration"),
    license="BSD",
    url="http://radiac.net/projects/sermin/",
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Installation/Setup',
    ],

    zip_safe=True,
    install_requires=[
        'future',
        'jinja2',
        'psutil',
        'six',
        'configparser',
    ],
    packages=find_packages(),
    include_package_data=True,
    extras_require={
        'dev':  [
            'nose',
            'flake8',
            'sphinx',
            'sphinx_rtd_theme',
        ],
    },
    test_suite='nose.collector',
    cmdclass={
        'vagrant': VagrantCommand,
    },
    entry_points={
        'console_scripts': [
            'sermin = sermin.bin:shell_exec',
        ]
    }
)
