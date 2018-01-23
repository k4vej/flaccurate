import os
import sys
import glob
import re
import logging
import argparse
import importlib
from pathlib import Path

import filetype as filemagic
import filetype.utils

import flaccurate.exception

class Base(object):
    """The Base class from which all flaccurate.commands.* should inherit.

Currently only one abstract method which needs overriding: run()

Implements the --usage output for each derived class, where they are expected
to have a docstring header unique to the class explaining what the command does
and any specific options required.
"""
    PLUGINS_PATH = 'plugins'

    def __init__(self, args):
        self.args = args

        # Recommended by Guido himself:
        # See: http://www.artima.com/weblogs/viewpost.jsp?thread=4829
        if( self.args.usage ):
            raise flaccurate.Usage(self.usage())

        self.debug = self.args.debug
        self.silent = self.args.silent
        self.quiet = self.args.quiet
        self.log_level = self._init_logging()
        logging.debug('Base __init__ %s', vars(self.args))

    def _init_logging(self):
        if( self.debug ):
            log_level = 'debug'
        elif( self.quiet ):
            log_level = 'warning'
        else:
            log_level = 'info'

        LEVELS = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }

        logging.basicConfig(
            level=LEVELS.get(
                log_level,
                logging.NOTSET
            ),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return log_level

    def _init_database(self):
        db = None
        try:
            db = flaccurate.Database(self.args)
        except RuntimeError as e:
            logging.critical('%s - exiting', e.args[0])
            sys.exit(1)
        return db

    def _init_plugins(self):
        logging.debug('_init_plugins( %s )', self.PLUGINS_PATH)
        return self._discover_plugins()

    def _discover_plugins(self):
        return {module_name.replace('flaccurate.plugins.',''): sys.modules[module_name]
                    for module_name in sys.modules.keys()
                        if( self._valid_plugin(module_name))}

    def _valid_plugin(self,module_name):
        if( module_name.startswith( 'flaccurate.plugins.' ) ):
            return True
        else:
            return False

    def supported_filetypes(self):
        return self.plugins.keys()

    def run(self):
        raise NotImplementedError('This is a base class - override me.')

    def usage(self):
        return self.__doc__
