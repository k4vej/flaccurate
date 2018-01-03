import logging
import mutagen
from mutagen.flac import FLAC

debug = False
log_level = 'debug' if debug else 'info'
testfile = './tests/test-data/01 - Mars, the Bringer of War.flac'

def setup_logging():
    LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
   
    logging.basicConfig( level=LEVELS.get(log_level, logging.NOTSET) )

def get_flac_md5_signature( filename ):
    md5 = False
    logging.debug('get_flac_md5_signature( %s )', testfile)
    try:
        audiofile = FLAC( filename )
        md5 = audiofile.info.md5_signature
    except mutagen.MutagenError as err:
        logging.debug( 'Failed to open %s: %s', filename, err )
    #if debug: print( vars( audiofile.info ) )
    return md5

setup_logging()
signature = get_flac_md5_signature( testfile )
if signature:
    logging.info( "%s: %s", testfile, signature )
else:
    logging.info( 'No md5 signature for %s - skipping', testfile )
