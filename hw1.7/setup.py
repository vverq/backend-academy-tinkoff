from setuptools import find_packages, setup

setup(
    name='tvbotlib',
    packages=find_packages(include=['tvbot']),
    version='0.1.0',
    description='telegram bot for get info about TV program',
    author='Me',
    license='MIT',
    install_requires=["requests", "pydantic"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)