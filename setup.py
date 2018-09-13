from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='more-minimal-plasma',
    version='0.0.1',
    description='Minimal Viable Plasma: Made More Minimal',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kfichter/more-minimal-plasma',
    author='ic3bootcamp',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3'
    ],
    keywords='plasma contracts ethereum minimal solidity',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'ethereum==2.3.0',
        'rlp==0.6.0',
        'py-solc==3.1.0',
        'web3==4.4.1'
    ]
)
