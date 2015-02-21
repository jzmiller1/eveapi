from distutils.core import setup

from eveapi import VERSION

setup(
    name='eveapi',
    version=VERSION,
    description='Python library for accessing the EVE Online API.',
    author='Jamie van den Berge',
    author_email='jamie@hlekkir.com',
    url='https://github.com/ntt/eveapi',
    keywords=('eve-online', 'api'),
    platforms='any',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Games/Entertainment',
    ),
    # CONTENTS
    zip_safe = True,
    py_modules = ['eveapi'],
)
