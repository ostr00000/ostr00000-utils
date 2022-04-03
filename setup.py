from setuptools import find_packages, setup

setup(
    name='ostr00000-utils',
    version='0.2',
    python_requires='>=3.8',
    description="Set of various frequently used functions, classes.",

    package_dir={'': 'lib'},
    packages=find_packages(exclude=('*test*',)),

    install_requires=['decorator', 'PyQt5'],
)
