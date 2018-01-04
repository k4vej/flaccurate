import os
import sys
import glob
import logging
import argparse

import sqlite3

import mutagen
from mutagen.flac import FLAC

supported_filetypes = [ 'flac' ]

def _argparse_init():
    # Note: most defaults are explicitly set to None
    # Setting fallback defaults is instead delayed until after
    # argparse is complete so that:
    # 1. Detection and explicit logging of this fact
    # 2. More complex decisions about what the default is can be done
    # See: _init()
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

    # Need to expose these for processing elsewhere
    # Only neater way is to make this a Class.
    # TODO: Consider refactoring into a Class.
    global args
    args = parser.parse_args()

    global debug
    debug = args.debug

def _logging_init():
    log_level = 'debug' if debug else 'info'

    LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    logging.basicConfig( level=LEVELS.get(log_level, logging.NOTSET) )

def _db_init( db_file ):
    logging.debug('_db_init( %s )', db_file)
    global dbh
    dbh = sqlite3.connect(db_file)
    dbh.execute("CREATE TABLE IF NOT EXISTS hashes(filename text PRIMARY KEY, md5 text NOT NULL, filetype text NOT NULL)")

def _db_insert_hash( data ):
    logging.debug('_db_insert_hash( %s )', data)
    # con.rollback() is called after the with block finishes with an exception, the
    # exception is still raised and must be caught
    try:
        with dbh:
            dbh.execute("INSERT INTO hashes(filename, md5, filetype) values (?, ?, ?)", (data.get('filename'), data.get('md5'), data.get('filetype')) )
    except sqlite3.IntegrityError:
        logging.error("Failed to insert into database")

def get_flac_md5_signature( filename ):
    logging.debug('get_flac_md5_signature( %s )', filename)
    md5 = None
    try:
        audiofile = FLAC( filename )
        md5 = audiofile.info.md5_signature
    except mutagen.MutagenError as err:
        logging.error( 'Failed to open file: %s', err )
    #if debug: print( vars( audiofile.info ) )
    logging.debug('get_flac_md5_signature( %s ) returning: %s', filename, str(md5))
    return str(md5)

def itterate_iglob( filetype ):
    logging.debug('itterate_iglob( %s )', filetype)
    for filename in glob.iglob(args.path + '**/*.' + filetype, recursive=True):
        _db_insert_hash({
            'filename' : filename,
            'md5' : get_flac_md5_signature(filename),
            'filetype' : filetype
        })


def _init():
    _argparse_init()
    _logging_init()
    logging.debug('args: %s', vars(args))

    if( args.path is None ):
        logging.info('No path specified - nothing TODO - exiting...');
            # implement checking for config elsewhere (file / env variable)
        sys.exit(0)
    else:
        if not(os.path.isdir(args.path)):
            logging.info('Specified path does not exist - exiting')
            sys.exit(0)

    db_file = './flaccurate.db'
    if( args.database is None ):
        logging.info('No database specified - defaulting to %s', db_file );
    else:
        logging.info('Using database specified: %s', args.database );
        db_file = args.database

    _db_init(db_file)


# setup all the basics
_init()

# recurse through all files and folders and determine the audio hash
for filetype in supported_filetypes:
    itterate_iglob(filetype)
