from setuptools import setup, find_packages
from version import __version__ as myVersion
import os, io

HERE = os.path.abspath(os.path.dirname(__file__))

def read(path, encoding="utf-8"):
    path = os.path.join(os.path.dirname(__file__), path)
    with io.open(path, encoding=encoding) as fp:
        return fp.read()

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

def get_install_requirements(path):
    content = read(path)
    return [req for req in content.split("\n") if req != "" and not req.startswith("#")]

setup(name='MOVE3',
      description='Maintence of Variance Toolbox',
      url='https://github.com/danhamill/MOVE3',
      download_url='https://github.com/danhamill/MOVE3',
      author='Daniel Hamill',
      author_email='daniel.d.hamill@usace.army.mil',
      packages=['move3.core'],
      python_requires='>3.9',
      install_requires=['altair<5', 'numpy', 'pandas', 'scikit_learn', 'setuptools', 'pytest'],
      classifiers=[
        "Development Status :: 4 - Beta",
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        "Topic :: Utilities",
      ],
      long_description=readme,
      tests_require=['pytest'],
      version = myVersion
      )
