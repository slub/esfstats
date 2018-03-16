"""
A Python3 program that extracts some statistics regarding field coverage from an elasticsearch index.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='esfstats',
      version='0.0.1',
      description='a Python3 program that extracts some statistics regarding field coverage from an elasticsearch index',
      url='https://github.com/slub/esfstats',
      author='Bernhard Hering',
      author_email='bernhard.hering@slub-dresden.de',
      license="Apache 2.0",
      packages=[
          'esfstats',
      ],
      package_dir={'esfstats': 'esfstats'},
      install_requires=[
          'argparse>=1.4.0',
          'elasticsearch>=5.0.0'
      ],
      entry_points={
          "console_scripts": ["esfstats=esfstats.esfstats:run"]
      }
      )
