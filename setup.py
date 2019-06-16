import os
from setuptools import setup
from quine_mccluskey import qm

m = qm.QuineMcCluskey

setup(
    name = "quine_mccluskey",
    version = m.__version__,
    author = "Thomas Pircher",
    author_email = "tehpeh-web@tty1.net",
    description = ("An implementation of the Quine-McCluskey algorithm"),
    license = "BSD",
    keywords = "Quine McCluskey, XOR",
    url = "https://github.com/tpircher/quine-mccluskey",
    download_url = 'https://github.com/tpircher/quine-mccluskey/releases/tag/v%s' % m.__version__,
    packages=['quine_mccluskey', 'tests'],
    long_description=open('README.md').read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
