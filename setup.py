from setuptools import setup, find_packages


# function to read dependencies from requirements.txt
def parse_requirements(filename):
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
    install_requires=parse_requirements('requirements.txt'),  # Dynamically load dependencies
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10'
)
