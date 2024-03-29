"""Buildbot module for latent digitalocean workers.

See:
https://github.com/johnramsden/buildbot-digitalocean-latent-worker
"""

# Prefer setuptools over distutils
from setuptools import setup

setup(
    name='digitalocean-latent-worker',

    version='0.0.2',

    description='Buildbot module for latent digitalocean workers',

    url='https://github.com/johnramsden/buildbot-digitalocean-latent-worker',

    author='John Ramsden',
    author_email='johnramsden@riseup.net',

    license='BSD-3-Clause',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # Common values:
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # License should match "license" above
        'License :: OSI Approved :: BSD License',

        # Python versions you supported.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    packages=['DigitalOceanLatentWorker'],

    entry_points={
        'buildbot.worker':
            ['DigitalOceanLatentWorker=DigitalOceanLatentWorker:DigitalOceanLatentWorker']
    },

    install_requires=[
        'python-digitalocean'
        'buildbot[bundle]'
    ],
)
