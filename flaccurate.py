import os
import sys
import glob
import re
import logging
import argparse
import importlib

import sqlite3


def main(args=None):
    """The main routine."""

    # For all supported filetypes,
    # recurse through the supplied path and determine the audio hash.
    # A supported filetype is determined by the presence of a
    # corresponding plugin for the file extension (see plugins folder).
    Flaccurate().process_all()


class Flaccurate:

    def __init__(self):
        self.args = self._init_argparse()
        self.debug = self.args.debug
        self.log_level = self._init_logging()
        logging.debug('args: %s', vars(self.args))

        self.db_file = './flaccurate.db'  # default unless specified
        self.plugins_path = 'plugins'

        if(self.args.path is None):
            logging.info('No path specified - nothing TODO - exiting...')
            # implement checking for config elsewhere (file / env variable)
            sys.exit(0)
        else:
            if not(os.path.isdir(self.args.path)):
                logging.info('Specified path does not exist - exiting')
                sys.exit(0)

        if(self.args.database is None):
            logging.info('No database specified - defaulting to %s', self.db_file)
        else:
            logging.info('Using database specified: %s', self.args.database)
            self.db_file = self.args.database

        self.dbh = self._init_db()
        self.plugins = self._init_plugins()

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
        log_level = 'debug' if self.debug else 'info'

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

    def _init_db(self):
        logging.debug('_init_db( %s )', self.db_file)
        dbh = sqlite3.connect(self.db_file)
        dbh.execute("CREATE TABLE IF NOT EXISTS hashes(filename text PRIMARY KEY, md5 text NOT NULL, filetype text NOT NULL)")
        return dbh

    def _init_plugins(self):
        logging.debug('_init_plugins( %s )', self.plugins_path)
        # Inspired by importdir by Aurelien Lourot
        # See: https://gitlab.com/aurelien-lourot/importdir
        plugins = {}
        sys.path.append(self.plugins_path) # adds provided path to paths we can import from
        for entry in os.listdir(self.plugins_path):
            if os.path.isfile(os.path.join(self.plugins_path, entry)):
                regexp_result = re.search("(.+)\.py(c?)$", entry)
                if regexp_result:  # found a module file name matching above regexp
                    module_name = regexp_result.groups()[0]
                    logging.debug('_init_plugins( %s ): Found plugin %s', self.plugins_path, module_name)
                    plugins[module_name] = importlib.import_module(module_name)
        return plugins

    def _db_insert_hash(self, data):
        logging.debug('_db_insert_hash( %s )', data)
        # con.rollback() is called after the with block finishes with an exception, the
        # exception is still raised and must be caught
        try:
            with self.dbh:
                self.dbh.execute("INSERT OR IGNORE INTO hashes(filename, md5, filetype) values (?, ?, ?)", (data.get('filename'), data.get('md5'), data.get('filetype')))
        except sqlite3.IntegrityError:
            logging.error("Failed to insert into database for: %s", data.get('filename'))

    def _itterate_iglob(self, filetype):
        logging.debug('itterate_iglob( %s )', filetype)
        count = 0
        for filename in glob.iglob(self.args.path + '**/*.' + filetype, recursive=True):
            count += 1
            self._db_insert_hash({
                'filename': filename,
                'md5': self.plugins[filetype].md5(filename),
                'filetype': filetype
            })
        logging.info('Processed %i %s files', count, filetype)

    def supported_filetypes(self):
        return self.plugins.keys()

    def process_filetype(self, filetype):
        self._itterate_iglob(filetype)

    def process_all(self):
        for filetype in self.supported_filetypes():
            self.process_filetype(filetype)

if __name__ == "__main__":
    main()
