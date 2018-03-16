"""
A Python3 program that extracts some statistics regarding field coverage in a line-delimited JSON document.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='python_esfstats',
      version='0.0.1',
      description='a Python3 program that extracts some statistics regarding field coverage from an elasticsearch index',
      url='https://github.com/slub/python-esfstats',
      author='Bernhard Hering',
      author_email='bernhard.hering@slub-dresden.de',
      license="Apache 2.0",
      packages=[
          'python_esfstats',
      ],
      package_dir={'python_esfstats': 'python_esfstats'},
      install_requires=[
          'argparse>=1.4.0',
          'elasticsearch>=5.0.0'
      ],
      entry_points={
          "console_scripts": ["python-esfstats=python_esfstats.python_esfstats:run"]
      }
      )
