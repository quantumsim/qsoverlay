#!/usr/bin/env python

import setuptools
from distutils.core import setup


setup(name='qsoverlay',
      version='0.1',
      description='An overlay of quantumsim for easier circuit building',
      author='Tom OBrien et al',
      author_email='obrien@lorentz.leidenuniv.nl',
      packages=['qsoverlay'],
      ext_package='qsoverlay',
      data_files=[],
      install_requires=["quantumsim", "pytools", "numpy>=1.12", "pytest", "matplotlib", "parsimonious"]
      )
