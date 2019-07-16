import os

from setuptools import find_packages
from setuptools import setup


def find_stubs(package):  # type: ignore
    stubs = []
    for root, _, files in os.walk(package):
        for f in files:
            path = os.path.join(root, f).replace(package + os.sep, '', 1)
            if path.endswith('.pyi') or path.endswith('py.typed'):
                stubs.append(path)
    return {package: stubs}


setup(
    name='pynamodb-attributes',
    version='0.2.5',
    description='Common attributes for PynamoDB',
    url='https://www.github.com/lyft/pynamodb-attributes',
    maintainer='Lyft',
    maintainer_email='ikonstantinov@lyft.com',
    packages=find_packages(exclude=['tests*']),
    dependency_links=[],
    install_requires=[
        "pynamodb>=3.3.3",
    ],
    python_requires='>=3',
    package_data=find_stubs('pynamodb_attributes'),
)
