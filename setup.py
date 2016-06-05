import os.path
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


exec(open('version.py').read())

setup(name='ranrot',
    version=__version__,
    description='Pseudo-random number generator showcase',
    long_description=read('README.md'),
    author='Bogdan Staicu',
    author_email='bogdan.staicu@gmail.com',
    url='https://github.com/BogdanStaicu/ranrot',
    include_package_data=True,
    classifiers=[],
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'tornado==4.3',
        'Pillow==2.3.0',
    ],
    setup_requires=[
        'pytest-runner==2.6.2',
    ],
    tests_require=[
        'pytest==2.8.2',
        'pytest-pep8==1.0.6',
        'pytest-cov==2.2.0',
    ])
