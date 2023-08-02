from setuptools import setup, find_packages
from version import __version__ as myVersion

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

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
      long_description=readme,
      tests_require=['pytest'],
      version = myVersion
      )
