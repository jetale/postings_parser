from setuptools import setup, find_packages

setup(
    name='postings_parser',
    version='0.1',
    packages=find_packages(),
    package_data={
        '': ['postings_parser/input/*.txt'],  # Include all CSV files under the 'data' directory
    },
)
