from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='plasma-battleship',
    version='0.0.1',
    description='Battleship: Plasma Edition',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kfichter/plasma-battleship',
    author='ic3bootcamp',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3'
    ],
    keywords='plasma contracts ethereum battleship solidity',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'ethereum==2.3.0',
        'rlp==0.6.0',
        'py-solc==3.1.0',
        'web3==4.4.1'
    ]
)
