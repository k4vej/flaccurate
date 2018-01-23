from .base import Base

import sys
import glob
from pathlib import Path

import filetype as filemagic
import filetype.utils

import logging
logging.getLogger(__name__)

class Curate(Base):
    """The curate command performs the real work of flaccurate.

Takes the given --input and calculates it checksum.
If an entry exists in the checksum database from a previous run,
it is compared to check for accuracy, any discrepancies are highlighted.

Usage:
    cli.py [--usage] curate

For general help:
    cli.py --help
"""
    def __init__(self,args):
        super().__init__(args)

    def run(self):
        self.db = self._init_database()
        self.plugins = self._init_plugins()

        if(self.args.input is None):
            raise flaccurate.Usage('No input specified - nothing TODO - exiting...')
            # implement checking for config elsewhere (file / env variable)
        else:
            if not(Path(self.args.input).is_dir()):
                logging.info('Specified input does not exist - exiting')
                sys.exit(0)

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
        
        self.process_all()

    def _calculate_checksum(self, filename, filetype):
        logging.debug('_calculate_checksum( %s, %s )', filename, filetype)
        return self.plugins[filetype].md5(filename)

    def _itterate_iglob(self, filetype):
        logging.debug('itterate_iglob( %s )', filetype)
        logging.info('Processing %s files', filetype)
        count = 0
        for filename in glob.iglob(self.args.input + '**/*.' + filetype, recursive=True):
            logging.info('%s: %s', filetype, filename)
            count += 1
            self._process_file(filename, filetype)

        logging.info('Processed %i %s files', count, filetype)

    def _valid_file(self, filename, filetype):
        logging.debug('_valid_file( %s, %s )', filename, filetype)
        # Delegate file validation to the filetype module.
        # Aliased to filemagic on import - already using a variable
        # called filetype throughout.

        # The filetype module does file magic checking in pure python,
        # so no deps or bindings on libmagic or anything else.
        # Interface is a bit clunky, considered duplicating its validation
        # logic in each plugin, but placing the one very awkward call here
        # means it will apply to every supported filetype (read: plugin)
        # without any additional work.
        #
        # 1. Retrieve a filemagic object of the type we want
        # to validate against.  Bit of a nightmare, as the function:
        # get_type() compares the "filetype" argument passed in,
        # against an enumerated list of filetypes, using is().
        # is() does not play nicely if the filetype argument takes the form
        # of a key from a dictionary - never matching against what looks like
        # identical strings.  Need to jump through an intern() hoop to get the
        # "correct string" for comparison.
        # 2. Using the filemagic object returned from step one above, via:
        # get_type() - call it's instance method: match() passing in the
        # appropriate bytes from the file being tested - this is where the
        # the magic happens..
        # The public API is at least helpful here, providing a utility function:
        # get_signature_bytes(filename)
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
                logging.debug('_process_file( %s, %s ): Checksum verified (%s)', filename, filetype, checksum_calculated)
            else:
                logging.warning('%s: %s - Failed checksum (Current: %s Previous: %s)', filetype, filename, checksum_calculated, checksum_record)
        else:
            logging.debug('_process_file( %s, %s ): Inserting checksum (%s)', filename, filetype, checksum_calculated)
            self.db._insert_checksum({
                'filename': filename,
                'md5': checksum_calculated,
                'filetype': filetype
            })

    def process_filetype(self, filetype):
        self._itterate_iglob(filetype)

    def process_all(self):
        for filetype in self.supported_filetypes():
            self.process_filetype(filetype)
