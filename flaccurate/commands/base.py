import sys

import flaccurate.exception

import logging
logging.getLogger(__name__)

class Base(object):
    """The Base class from which all flaccurate.commands.* should inherit.

Currently only one abstract method which needs overriding: run()

Implements the --usage output for each derived class, where they are expected
to have a docstring header unique to the class explaining what the command does
and any specific options required.
"""
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
        plugins = None
        try:
            plugins = flaccurate.Plugins(self.args)
        except RuntimeError as e:
            logging.critical('%s - exiting', e.args[0])
            sys.exit(1)
        return plugins

    def run(self):
        raise NotImplementedError('This is a base class - override me.')

    def usage(self):
        return self.__doc__
