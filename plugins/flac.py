import logging
logging.getLogger(__name__)

import mutagen
from mutagen.flac import FLAC 

def md5( filename ):
    logging.debug('get_flac_md5_signature( %s )', filename)
    md5 = None
    try:
        audiofile = FLAC( filename )
        # mutagen.flac.FLAC.info() provides access to all content
        # from the STREAMINFO block in flac header.  The docs do not
        # mention md5_signature specifically, but looking at the content
        # of the StreamInfo object returned by the info() method it
        # contains an md5_signature attribute.
        # print( vars( audiofile ) )
        # See: http://mutagen.readthedocs.io/en/latest/api/flac.html?highlight=FLAC
        #
        # The value stored in the STEAMINFO block is a 16 byte field hex field.
        # This gets decoded using the format string %02x
        # Zero padding seems to be getting stripped from formatted output,
        # so fixed with an rjust() to zero pad upto the max length of an md5
        # string of 32 characters.
        md5 = ( "%02x" % audiofile.info.md5_signature ).rjust(32,'0')
    except mutagen.MutagenError as err:
        print("error")
        logging.error( 'Failed to open file: %s', err )
#    print( vars( audiofile.info ) )
    logging.debug('get_flac_md5_signature( %s ) returning: %s', filename, str(md5))

    # Explicitly cast this to string so we do not end up with any ambiguity
    # over it being a really long number. During db insertion, the duck typing
    # which an sqlite column is subject to, has resulted in problems with
    # what looks like an md5sum value looking like a massive integer causing 
    # integer overflow errors
    return md5

