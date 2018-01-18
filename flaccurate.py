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

import flaccurate

def main(args=None):
    # For all supported filetypes,
    # recurse through the supplied path and determine the audio hash.
    # A supported filetype is determined by the presence of a
    # corresponding plugin for the file extension (see plugins folder).

    # Operation as follows:
    # For each supported file type (read: plugin) (see: process_filetype())
    # For each matching file found in file type (see: itterate_iglob())
    # Calculate the audio md5 checksum: (see: _process_file())
    # 1. If the database record exists for file (see: Database._retrieve_checksum())
    #       Compare new checksum against database record (see: _process_file())
    #           If checksum matches all good
    #           If checksum doesn't match report it
    # 2. If the database has no record of file - insert it for first time (see: Database._insert_checksum())

    Flaccurate().process_all()


class Flaccurate:
    PLUGINS_PATH = 'plugins'

    def __init__(self):
        self.args = self._init_argparse()
        self.debug = self.args.debug
        self.silent = self.args.silent
        self.log_level = self._init_logging()
        logging.debug('args: %s', vars(self.args))

        try:
            self.db = flaccurate.Database(self.args)
        except RuntimeError as e:
            logging.critical('%s - exiting', e.args[0])
            sys.exit(1)

        self.plugins = self._init_plugins()

        # Perform no file processing - but quit after all
        # initialisation and plugin loading
        if(self.args.selfcheck):
            logging.info('Self check complete - exiting...')
            sys.exit(0)

        if(self.args.path is None):
            logging.info('No path specified - nothing TODO - exiting...')
            # implement checking for config elsewhere (file / env variable)
            sys.exit(0)
        else:
            if not(os.path.isdir(self.args.path)):
                logging.info('Specified path does not exist - exiting')
                sys.exit(0)


    def _init_argparse(self):
        # Note: most defaults are explicitly set to None
        # Setting fallback defaults is instead delayed until after
        # argparse is complete so that:
        # 1. Detection and explicit logging of this fact
        # 2. More complex decisions about what the default is can be done
        # See: __init__()
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-d', '--debug',
            help='enable debug', action='store_true'
        )
        parser.add_argument(
            '-s', '--silent',
            help='silent mode - will only output warnings or errors', action='store_true'
        )
        parser.add_argument(
            '-c', '--selfcheck',
            help='performs all initialisation and plugin loading then exits', action='store_true'
        )
        parser.add_argument(
            'path',
            nargs='?',
            type=str,
            default=None,
            help='specify directory where audio files are stored'
        )
        parser.add_argument(
            '-db', '--database',
            nargs='?',
            type=str,
            default=None,
            help='specify the database file to use',
        )
        return parser.parse_args()

    def _init_logging(self):
        if( self.debug ):
            log_level = 'debug'
        elif( self.silent ):
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

    def _init_plugins(self):
        logging.debug('_init_plugins( %s )', self.PLUGINS_PATH)
        # Inspired by importdir by Aurelien Lourot
        # See: https://gitlab.com/aurelien-lourot/importdir
        plugins = {}

        for module_name, imported_module in sys.modules.items():
            if( module_name.startswith( 'flaccurate.plugins.' ) ):
                plugin_name = module_name.replace('flaccurate.plugins.','')
                logging.debug('_init_plugins( %s ): Found plugin %s', self.PLUGINS_PATH, plugin_name)
                plugins[plugin_name] = sys.modules[module_name]

        return plugins

    def _calculate_checksum(self, filename, filetype):
        logging.debug('_calculate_checksum( %s, %s )', filename, filetype)
        return self.plugins[filetype].md5(filename)

    def _itterate_iglob(self, filetype):
        logging.debug('itterate_iglob( %s )', filetype)
        logging.info('Processing %s files', filetype)
        count = 0
        for filename in glob.iglob(self.args.path + '**/*.' + filetype, recursive=True):
            logging.info('%s: %s', filetype, filename)
            count += 1
            self._process_file(filename, filetype)

        logging.info('Processed %i %s files', count, filetype)

    def _valid_file(self, filename, filetype):
        logging.debug('_valid_file( %s, %s )', filename, filetype)
        # Delegate file validation to the filetype module, has been#
        # alias'd to filemagic on import - so it doesn't clash with
        # our own internal references to a filetype variable.
        # The filetype module does file magic checking in pure python,
        # so no deps or bindings on libmagic or anything else.
        # Interface is a bit clunky, considered duplicating its validation
        # logic in each plugin, but placing the one very awkward call here
        # means it will apply to every supported filetype (read: plugin)
        # without any additional work.
        #
        # 1. We first need to retrieve a filemagic object of the type we want
        # to validate against.  This in itself is a nightmare, as the
        # get_type() function compares the argumenet passed in against its
        # enumerated list of filetypes uses is() which does not play nicely
        # with the argument we are passing ("filetype"), as it takes the form
        # of a key from a dictionary.  So was never matching against its own
        # extension string - need to jump through an intern() hoop to get the
        # "correct string" for comparison.
        # 2. We then need to pass in the appropriate bytes from the file being
        # tested, so that the match() function can do its magic work.
        # Return from match() is Boolean, so just pass it back to caller.
        return filemagic.get_type(None,sys.intern(filetype)).match( filemagic.utils.get_signature_bytes( filename ) )

    def _process_file(self, filename, filetype):
        logging.debug('_process_file( %s, %s )', filename, filetype)

        if(not self._valid_file(filename, filetype)):
            logging.info('Skipping invalid %s: %s', filetype, filename)
            return

        checksum_calculated = self._calculate_checksum( filename, filetype )
        checksum_record = self.db._retrieve_checksum( filename )

        if( checksum_record is not None ):
            if( checksum_calculated == checksum_record ):
                logging.debug('_process_file( %s, %s ): Checksum verified', filename, filetype)
            else:
                logging.warning('%s: %s - Failed checksum (Current: %s Previous: %s)', filetype, filename, checksum_calculated, checksum_record)
        else:
            logging.debug('_process_file( %s, %s ): Inserting new checksum', filename, filetype)
            self.db._insert_checksum({
                'filename': filename,
                'md5': checksum_calculated,
                'filetype': filetype
            })

    def supported_filetypes(self):
        return self.plugins.keys()

    def process_filetype(self, filetype):
        self._itterate_iglob(filetype)

    def process_all(self):
        for filetype in self.supported_filetypes():
            self.process_filetype(filetype)

if __name__ == "__main__":
    main()
