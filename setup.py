from setuptools import find_packages, setup

setup(
    name='ostr00000-utils',
    version=0.1,
    python_requires='>=3.8',
    description='Set of various frequently used functions, classes.',
    packages=find_packages(exclude=("*test*",)),
    entry_points={'console_scripts': []},
    package_dir={"": "lib"},
    install_requires=['decorator', 'PyQt5'],
    extras_require={},
)
