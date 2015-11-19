#! /usr/bin/env python

import glob
from distutils.core import setup

scripts = glob.glob( "scripts/i*" )

setup( name = 'mcia-irods-utils',
       version = '0.5.7',
       description = 'MCIA\'s iCommands utilities',
       author = 'Pierre Gay',
       author_email = 'pierre.gay@u-bordeaux.fr',
       url = 'https://github.com/mesocentre-mcia/mcia-irods-utils',
       packages = ['mcia_irods_utils', ],
       scripts = scripts ,
     )
