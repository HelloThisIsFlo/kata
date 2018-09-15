from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='kata',
    version='0.0.1',
    description='Kata made easy: A TDD setup in the language of your choice in a single command',
    long_description=readme(),
    keywords='test tdd kata clean-code home-automation softwarecrafter',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
        'Topic :: Software Development :: Testing'
    ],
    url='https://floriankempenich.github.io/kata',
    author='Florian Kempenich',
    author_email='Flori@nKempenich.com',
    packages=['kata'],
    license='MIT',
    scripts=['bin/kata'],
    install_requires=[
        'click'
    ],
    include_package_data=True
)
