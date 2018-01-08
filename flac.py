import mutagen
from mutagen.flac import FLAC 

class Flac:
    def __init__( self, filename ):
        self._filename = filename
        self._md5 = None 

    def __str__( self ):
        return self.filename + ': ' + self.md5

    def md5( self ):
        #hlogging.debug('get_flac_md5_signature( %s )', filename)
        md5 = None
        try:
            audiofile = FLAC( self._filename )
            self._md5 = str(audiofile.info.md5_signature)
        except mutagen.MutagenError as err:
            print("error")
            #logging.error( 'Failed to open file: %s', err )
        #if debug: print( vars( audiofile.info ) )
        #logging.debug('get_flac_md5_signature( %s ) returning: %s', filename, str(md5))

        # Explicitly cast this to string so we do not end up with any ambiguity
        # over it being a really long number. During db insertion, the Pythonic
        # duck typing an sqlite column is subject to has resulted in problems with
        # what looks like an md5sum value looking like a massive integer causing INT overflow errors
        return self._md5

