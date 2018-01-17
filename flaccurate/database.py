import sqlite3
from pathlib import Path

import logging
logging.getLogger(__name__)

class Database:
    DEFAULT_DB_FILE = 'flaccurate.db'

    def __init__(self, args):
        self.debug = args.debug
        self.silent = args.silent
        self.args = args
        logging.debug('Database __init__ args: %s', vars(self.args))

        if(args.database is not None):
            logging.info('Database specified: %s', args.database)
            if( Path(args.database).is_file() ):
                self.db_file = args.database
            else:
                # TODO: THis should raise a file not found exception instead of continuing.
                # If you specify a database that is not available we should not try to do anything
                # else.  Maybe introduce a --force flag which continues through errors.
                logging.error('Database specified not found - defaulting to %s', self.DEFAULT_DB_FILE)
                self.db_file = self.DEFAULT_DB_FILE
        else:
            logging.info('Database not specified - defaulting to %s', self.DEFAULT_DB_FILE)
            self.db_file = self.DEFAULT_DB_FILE

        self.dbh = self._init_db()

    def _init_db(self):
        logging.debug('_init_db( %s )', self.db_file)

        db_exists = Path(self.db_file).is_file()
        if( db_exists ):
            logging.debug('_init_db( %s ): Database file found', self.db_file)
            if( not self._valid_db() ):
                raise RuntimeError('Database is not valid')
        else:
            logging.debug('_init_db( %s ): Database file not found, initialising', self.db_file)

        dbh = sqlite3.connect(self.db_file)
        dbh.execute("CREATE TABLE IF NOT EXISTS checksums(filename text PRIMARY KEY, md5 text NOT NULL, filetype text NOT NULL)")
        return dbh

    # Validation functions should be treated special -
    # they should return instantly on failure - not continue
    # needlessly performing additional checks
    def _valid_db(self):
        logging.debug('_valid_db( %s )', self.db_file)

        with sqlite3.connect(self.db_file) as dbh:
            integrity_results = dbh.execute("PRAGMA integrity_check").fetchone()

            if( integrity_results is not None ):
                if( integrity_results[0] != 'ok' ):
                    logging.critical('_valid_db( %s ): Integrity check failed', self.db_file)
                    return False
            else:
                logging.critical('_valid_db( %s ): Failed to obtain integrity results', self.db_file)
                return False

        return True
    
    def _insert_checksum(self, data):
        logging.debug('_insert_checksum( %s )', data)
        # con.rollback() is called after the with block finishes with an exception, the
        # exception is still raised and must be caught
        try:
            with self.dbh:
                self.dbh.execute("INSERT OR IGNORE INTO checksums(filename, md5, filetype) values (?, ?, ?)", (data.get('filename'), data.get('md5'), data.get('filetype')))
        except sqlite3.IntegrityError:
            logging.error("Failed to insert into database for: %s", data.get('filename'))

    def _retrieve_checksum(self, filename):
        logging.debug('_retrieve_checksum( %s )', filename)
        checksum = None

        results = self.dbh.execute('SELECT md5 FROM checksums WHERE filename=?', (filename,)).fetchone()

        if( results is not None ):
            checksum = results[0]
        else:
            logging.debug('_retrieve_checksum( %s ): No checksum found', filename)

        logging.debug('_retrieve_checksum( %s ): Returning %s', filename, checksum)
        return checksum
