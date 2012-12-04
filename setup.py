import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "quine_mccluskey",
    version = "0.1",
    author = "Thomas Pircher",
    author_email = "tehpeh@gmx.net",
    description = ("An implementation of the Quine-McCluskey algorithm"),
    license = "BSD",
    keywords = "Quine McCluskey, XOR",
    url = "http://www.tty1.net/quine-mccluskey/",
    packages=['quine_mccluskey', 'tests'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
