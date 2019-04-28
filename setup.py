#!/usr/bin/env python3

import re
import setuptools
import shutil

shutil.copyfile('ddgr', 'ddgr.py')

with open('ddgr.py', encoding='utf-8') as fp:
    version = re.search(r'_VERSION_ = \'(.*?)\'', fp.read()).group(1)

setuptools.setup(
    name='ddgr',
    version=version,
    url='https://github.com/jarun/ddgr',
    license='GPLv3',
    author='Arun Prakash Jana',
    author_email='engineerarun@gmail.com',
    description='DuckDuckGo from the terminal',
    long_description='See https://github.com/jarun/ddgr#readme.',
    python_requires='>=3.5',
    platforms=['any'],
    py_modules=['ddgr'],
    entry_points={
        'console_scripts': [
            'ddgr = ddgr:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Utilities',
    ],
)
