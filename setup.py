from setuptools import setup
import os
import io
import runpy

current = os.path.realpath(os.path.dirname(__file__))

with io.open(os.path.join(current, 'README.rst'), encoding="utf-8") as f:
    long_description = f.read()

with open(os.path.join(current, 'requirements.txt')) as f:
    install_requirements = f.read().splitlines()

__version__ = runpy.run_path(
    os.path.join(current, "mailparser", "version.py"))["__version__"]

setup(name='vaultfs',
      description='Hashicorp Vault fuse filesystem',
      url='https://github.com/PsyanticY/vaultfs',
      long_description=long_description,
      version=__version__,
      author='PsyanticY',
      author_email='iuns@outlook.fr',
      license='MIT',
      packages=['vaultfs'],
      platforms=["Linux"],
      install_requires=install_requirements,
      zip_safe=False)
