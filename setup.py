from setuptools import setup, find_packages


def parse_requirements(filename):
    """Function to read dependencies from requirements.txt"""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


setup(
    name='falgueras',
    version='0.1.1',
    author='Aleix Falgueras Casals',
    author_email='falguerasaleix@gmail.com',
    description='Common code for Python projects involving GCP, Pandas, and Spark.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/aleixfalgueras/falgueras',
    packages=find_packages(),
    install_requires=[
        "colorama~=0.4.6",
        "pytz~=2024.1",
        "pandas~=2.2.2",
        "db-dtypes~=1.3.1",
        "numpy~=2.2.1",
        "google-api-core~=2.24.0",
        "google-auth~=2.37.0",
        "google-cloud-bigquery~=3.27.0",
        "google-cloud-bigquery-storage~=2.27.0",
        "google-cloud-storage~=2.19.0",
        "google-api-python-client~=2.156.0",
        "google-cloud-secret-manager~=2.22.0",
        "google-cloud-language~=2.16.0",
        "protobuf~=5.29.2",
        "requests~=2.32.3"
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10'
)
