"""Setup to support installation as Python library"""
from setuptools import setup

setup(name='idsse',
      version='1.0',
      description='IDSSe Common',
      url='',
      author='WIDS',
      author_email='@noaa.gov',
      license='MIT',
      python_requires=">=3.11",
      packages=['idsse.common'],
      # packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
      install_requires=[
        'pint',
        'importlib_metadata',
        ],
      extras_require={
        'develop': [
          'pytest',
          'pytest-cov',
        ]
      },
      zip_safe=False)
