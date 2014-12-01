#! /usr/bin/env python

import os.path
import glob
from distutils.core import setup

setup( name = 'mcia-irods-password',
       version = '0.2',
       description = 'MCIA\'s iCommands utilities',
       author = 'Pierre Gay',
       author_email = 'pierre.gay@u-bordeaux.fr',
       url = 'https://github.com/mesocentre-mcia/mcia-irods-utils',
       packages = ['mcia_irods_utils', ],
       scripts = ['scripts/idu'] + glob.glob('icmdw/i*'),
     )
