from setuptools import find_packages
from setuptools import setup

setup(
    name='pynamodb-attributes',
    version='0.3.0',
    description='Common attributes for PynamoDB',
    url='https://www.github.com/lyft/pynamodb-attributes',
    maintainer='Lyft',
    maintainer_email='ikonstantinov@lyft.com',
    packages=find_packages(exclude=['tests*']),
    dependency_links=[],
    install_requires=[
        "pynamodb>=5.0.0",
    ],
    python_requires='>=3',
    package_data={'pynamodb_attributes': ['py.typed']},
)
