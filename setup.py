from setuptools import find_packages, setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='kata',
    version='0.0.9',
    description='Kata made easy: A TDD setup in the language of your choice in a single command',
    long_description=readme(),
    keywords='test tdd kata clean-code softwarecraft',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
        'Topic :: Software Development :: Testing'
    ],
    url='https://floriankempenich.github.data/kata',
    author='Florian Kempenich',
    author_email='Flori@nKempenich.com',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    license='MIT',
    scripts=['bin/kata'],
    install_requires=[
        'click',
        'requests'
    ],
    include_package_data=True
)
