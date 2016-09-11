import os
from setuptools import setup, find_packages

requirements = []
with open(os.path.sep.join([os.path.dirname(os.path.abspath(__file__)), 'requirements.txt']), 'rb') as fd:
    for l in fd:
        requirements.append(l)

setup(
    name='qualify_friend_inviter',
    version='1.0.0',
    description='Job offer qualification application making an invite sending and processing',
    author='Andy S',
    author_email='TOP SECRET',
    url='',
    install_requires=requirements,
    packages=find_packages(exclude=['test']),
    include_package_data=False,
    zip_safe=True,
    test_suite='test'
)
