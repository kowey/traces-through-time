"""
traces-through-time setup: support for the traces through time
research project
"""

from setuptools import setup, find_packages
from itertools import chain
from os import path as fp
import glob
import os

REQS = \
    ['html',
     'python-dateutil',
     'nltk']


def concat_l(iters):
    ':: [[a]] -> [a]'
    return list(chain.from_iterable(iters))

SCRIPT_DIRS = ['converters', 'evaluation']
SCRIPT_STAR = concat_l(glob.glob(fp.join(x, '*')) for x in SCRIPT_DIRS)

setup(name='traces-through-time',
      version='0.2',
      author='Eric Kow',
      author_email='eric@erickow.com',
      packages=find_packages(),
      scripts=[f for f in SCRIPT_STAR if not os.path.isdir(f)],
      install_requires=REQS)
