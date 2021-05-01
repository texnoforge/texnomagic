import setuptools


# get version
exec(open('texnomagic/__init__.py').read())


setuptools.setup(
    version=__version__)
