from setuptools import setup, find_packages

setup(
    name='falgueras',
    version='0.1.0',
    author='Aleix Falgueras Casals',
    author_email='falguerasaleix@gmail.com',
    description='Common code for Python projects involving GCP, Pandas, and Spark. ',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my_library',  # Optional: URL to your repository
    packages=find_packages(),
    install_requires=[
        # Add dependencies here, e.g., 'numpy>=1.21.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',  # Minimum Python version
)
