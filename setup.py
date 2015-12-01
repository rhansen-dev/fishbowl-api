from setuptools import setup
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='fishbowl-api',
    version='0.1',
    description='Fishbowl API',
    long_description=long_description,
    url='http://github.com/SmileyChris/fishbowl-api',
    author='Chris Beaven',
    author_email='smileychris@gmail.com',
    license='MIT',
    packages=['fishbowl'],
)
