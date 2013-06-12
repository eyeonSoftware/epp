#!/usr/bin/env python

import os
from setuptools import setup, find_packages

import epp.__INFO__ as INFO

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()
def read_firstline(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).readline()

setup(name='epp',
      version = INFO.__VERSION__,
      description = INFO.__NAME__,
      author = read_firstline('AUTHORS'),
      author_email = 'blazej{0}eyeonline{1}'.format(chr(60+4) ,".com"),
      url = INFO.__HELP__, 
      packages = find_packages(exclude=['tests']),
      scripts=['epp/bin/epp_install.py'],
      long_description = read('README'),
      license = INFO.__LICENSE__,
      install_requires=[
          'BeautifulSoup>=3.0', 
          "PySide>1.1.1", 
          #"PeyeonScript>6.2",
          "pywin32",
          ],
      platforms = ["win32"],
      #data_files=[('', ['README', 'AUTHORS', 'LICENSE'])],
      package_data = { '': [
          '_templates/*.*', 
          "_templates/project_dirs/*.*",
          "_templates/shot_dirs/*.*",
          "_templates/images/*.*",
          '_scripts/*.*', 
          '_scripts/fu/*.*', 
          '_scripts/fu/epp/*.*', 
          '_scripts/*.*', 
          '_scripts/gen/*.*', 
          '_scripts/gen/epp/*.*', 
          ],
          },
      
     )

