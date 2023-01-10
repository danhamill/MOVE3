from setuptools import setup, find_packages
from version import __version__ as myVersion

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='MOVE3',
      description='Maintence of Variance Toolbox',
      url='https://github.com/danhamill/MOVE3',
      author='Daniel Hamill',
      author_email='daniel.d.hamill@usace.army.mil',
      packages=find_packages(),
      python_requires='>3.9',
      install_requires=required,
      keywords=['hydrology', 'record extension', 'statistics',
                ],
      tests_require=['pytest'],
      version = myVersion
      )