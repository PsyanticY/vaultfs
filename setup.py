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
    os.path.join(current, "vaultfs", "version.py"))["__version__"]

setup(name='vaultfs',
      description='Hashicorp Vault fuse filesystem',
      url='https://github.com/PsyanticY/vaultfs',
      long_description=long_description,
      version=__version__,
      author='PsyanticY',
      author_email='iuns@outlook.fr',
      license='MIT',
      platforms=["Linux"],
      packages=["vaultfs"],
      install_requires=install_requirements,
      data_files =[('/etc', ['config/vaultfs.cfg'])],
      classifiers=[
        'Development Status :: 1 - Development',
        'Intended Audience :: Security/Automation',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only'
        ],
      keywords='Security HashicCorpVault keys fuse',
      entry_points = {
         'console_scripts': [
            'vaultfs = vaultfs.vaultfs:main',
         ],
       },
      zip_safe=False)
