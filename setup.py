#! /usr/bin/env python3
from distutils.core import setup
setup(
  name = 'automatool',
  packages = ['automatool'],
  version = '0.1.6',
  license='MIT',
  description = 'Automaton analysis and maniplation tool',
  author = 'Lucas Vinicius Hartmann',
  author_email = 'lucas.hartmann@gmail.com',
  url = 'https://github.com/lhartmann/python_automatool',
  download_url = 'https://github.com/lhartmann/python_automatool/archive/0.1.6.tar.gz',
  keywords = ['discrete events', 'automaton', 'state machine'],
  install_requires=[ 'pandas' ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
  ],
)
