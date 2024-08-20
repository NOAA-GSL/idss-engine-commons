"""Setup to support installation as Python library"""
import glob
from setuptools import setup

setup(name='idsse',
      version='1.0',
      description='IDSSe Common',
      url='',
      author='WIDS',
      author_email='@noaa.gov',
      license='MIT',
      python_requires=">=3.11",
      packages=['idsse.common', 'idsse.common.schema', 'idsse.common.sci'],
      data_files=[('idsse/common/schema', glob.glob('idsse/common/schema/*.json')),
                  ('idsse/common/sci/resources', glob.glob('idsse/common/sci/resources/*.json'))],
      include_package_data=True,
      package_data={'':['schema/*.json']},
      install_requires=[
        'pint',
        'importlib_metadata',
        'pika',
        'jsonschema',
        'python-logging-rabbitmq'
      ],
      extras_require={
        'develop': [
          'pytest',
          'pytest-cov',
        ]
      },
      zip_safe=False,
)
