from distutils.core import setup

setup(
    name='nerdouts',
    version='0.1dev',
    packages=['nerdouts'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    scripts=['nerdouts/workout'],
    data_files=[('.', ['README.md'])],
    long_description=open('README.md').read(),
    url='https://github.com/dseisun/nerdouts'
)