import sqlite3
import json
import hashlib
from pathlib import Path

import logging
logging.getLogger(__name__)

class Database:
    DEFAULT_DB_FILE = 'flaccurate.db'

    def __init__(self, args):
        self.debug = args.debug
        self.silent = args.silent
        self.force = args.force
        self.args = args
        logging.debug('Database __init__ args: %s', vars(self.args))

        if(args.database is not None):
            logging.info('Database specified: %s', args.database)
            self.db_file = args.database
        else:
            logging.info('Database not specified - defaulting to: %s', self.DEFAULT_DB_FILE)
            self.db_file = self.DEFAULT_DB_FILE

        if(Path(self.db_file).is_file()):
            logging.info('Database found: %s', self.db_file)
        elif(self.force):
            logging.info('Database not found - forcing creation: %s', self.db_file)
        elif(self.db_file == self.DEFAULT_DB_FILE):
            # This is here for convenience of first time users omitting options.
            # At least do something on the initial invokation instead of complain
            # about database filenames not existing.
            logging.info('Database not found - inaugural launch, creating: %s', self.db_file)
        else:
            # Specified database not found do nothing - don't try and guess what
            # is intended. If user wants to continue wuth a custom db name there is a
            # --force flag
            logging.info('Database not found: %s - use --force to create it', self.db_file)
            raise RuntimeError('Database not found')

        self.db_md5_file = self.db_file + '.md5'
        self.dbh = self._init_db()

    def _init_db(self):
        logging.debug('_init_db( %s )', self.db_file)

        # Only try to validate existing database
        db_exists = Path(self.db_file).is_file()
        if(db_exists):
            logging.debug('_init_db( %s ): Database file found', self.db_file)
            logging.info('Validating %s', self.db_file)
            if(self._valid_db()):
                logging.info('Database is valid')
            else:
                raise RuntimeError('Database is not valid')
        else:
            logging.debug('_init_db( %s ): Database file not found, initialising', self.db_file)
            self.checksum = None

        # Always perform table creation and checksum update -
        # Ensures a known starting point - rather than assuming the content exists in the file
        #
        # Not wrapped in a context manager:
        # 1. Want to return the db handle to constructor, not garbage collect it -
        #    so it is preserved as object attribute in self, for future use
        # 2. No transaction commit or rollback required on the initial creation of the table
        dbh = self._connect_db()
        dbh.execute("CREATE TABLE IF NOT EXISTS checksums(filename text PRIMARY KEY, md5 text NOT NULL, filetype text NOT NULL)")
        self._update_db_checksum()

        return dbh

    def _connect_db(self):
        dbh = None
        try:
            dbh = sqlite3.connect(self.db_file)
        except sqlite3.OperationalError as e:
            logging.debug('_connect_db(): Failed to connect to %s: %s', self.db_file, e.args[0])
            raise RuntimeError('Failed to connect to database')

        return dbh

    # Returns instantly on any validation failure
    # Performs two checks:
    # 1. Internal sqlite integrity_check
    # 2. Standalone checksum of the entire db_file
    def _valid_db(self):
        logging.debug('_valid_db( %s )', self.db_file)

        if(self._db_integrity_verified() and
            self._db_checksum_verified()):
            return True
        else:
            return False

    def _db_integrity_verified(self):
        try:
            with self._connect_db() as dbh:
                integrity_results = dbh.execute("PRAGMA integrity_check").fetchone()
        except sqlite3.OperationalError as e:
            logging.critical('_valid_db( %s ): Failed to perform database integrity check', self.db_file)
        else:
            if(integrity_results is not None):
                if(integrity_results[0] == 'ok'):
                    logging.info('Database integrity verified')
                    return True
                else:
                    logging.critical('_valid_db( %s ): Database integrity failure', self.db_file)
            else:
                logging.critical('_valid_db( %s ): Failed to obtain database integrity results', self.db_file)

        return False

    def _db_checksum_verified(self):
        if(Path(self.db_md5_file).is_file()): # make sure it exists first
            db_checksum_calculated = self._calculate_db_checksum()
            db_checksum_record = self._retrieve_db_checksum()

            if(db_checksum_calculated is None or
                db_checksum_record is None):
                return False

            if(db_checksum_calculated == db_checksum_record):
                logging.info('Database checksum verified')
                self.checksum = db_checksum_calculated
                return True
            else:
                logging.critical('_valid_db( %s ): Database checksum failure (Current: %s Previous: %s)', self.db_file, db_checksum_calculated, db_checksum_record)
        else:
            logging.critical('_valid_db( %s ): Database checksum file not found %s', self.db_file, self.db_md5_file)

        return False
    
    def _insert_checksum(self, data):
        logging.debug('_insert_checksum( %s )', data)
        # con.rollback() is called after the with block finishes with an exception, the
        # exception is still raised and must be caught
        try:
            with self.dbh:
                self.dbh.execute("INSERT OR IGNORE INTO checksums(filename, md5, filetype) values (?, ?, ?)", (data.get('filename'), data.get('md5'), data.get('filetype')))
        except (sqlite3.IntegrityError, sqlite3.OperationalError) as e:
            logging.error("Failed to insert %s into database: %s", data.get('filename'), e.args[0])
        else:
            self._update_db_checksum()

    def _retrieve_checksum(self, filename):
        logging.debug('_retrieve_checksum( %s )', filename)
        checksum = None

        results = self.dbh.execute('SELECT md5 FROM checksums WHERE filename=?', (filename,)).fetchone()

        if(results is not None):
            checksum = results[0]
        else:
            logging.debug('_retrieve_checksum( %s ): No checksum found', filename)

        logging.debug('_retrieve_checksum( %s ): Returning %s', filename, checksum)
        return checksum

    def _calculate_db_checksum(self):
        logging.debug('_calculate_db_checksum( %s )', self.db_file)
        checksum = None

        try:
            db_fileh = open(self.db_file, 'rb')
        except IOError as e:
            logging.critical('_calculate_db_checksum( %s ): Failed to calculate database checksum %s', self.db_file, e.args[0])
        else:
            hasher = hashlib.md5()
            hasher.update(db_fileh.read())
            checksum = str(hasher.hexdigest())
            db_fileh.close()

        logging.debug('_calculate_db_checksum( %s ): Returning %s', self.db_file, checksum)
        return checksum

    def _retrieve_db_checksum(self):
        logging.debug('_retrieve_db_checksum( %s )', self.db_md5_file)
        checksum = None

        try:
            db_md5_fileh = open(self.db_md5_file, 'r')
        except IOError as e:
            logging.critical('_retrieve_db_checksum( %s ): Failed to retrieve database checksum %s', self.db_md5_file, e.args[0])
        else:
            md5_file_content = json.load(db_md5_fileh)
            checksum = md5_file_content[self.db_file]['md5']
            db_md5_fileh.close()

        logging.debug('_retrieve_db_checksum( %s ): Returning %s', self.db_md5_file, checksum)
        return checksum

    def _insert_db_checksum(self, data):
        logging.debug('_insert_db_checksum( %s ): %s', self.db_md5_file, data)

        try:
            db_md5_fileh = open(self.db_md5_file, 'w')
        except IOError as e:
            logging.critical('_insert_db_checksum( %s ): Failed to insert database checksum %s', self.db_md5_file, e.args[0])
        else:
            json.dump(data, db_md5_fileh)
            db_md5_fileh.close()

    def _update_db_checksum(self):
        logging.debug('_update_db_checksum( %s )', self.db_md5_file)

        # Only update if its changed
        db_checksum_calculated = self._calculate_db_checksum()
        if(db_checksum_calculated != self.checksum):
            logging.debug('_update_db_checksum( %s ): Database checksum updated %s', self.db_md5_file, db_checksum_calculated)
            self._insert_db_checksum({
                self.db_file : {
                    'md5' : db_checksum_calculated
                }
            })
