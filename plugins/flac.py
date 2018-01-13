import hashlib
import audiotools
import mutagen
from mutagen.flac import FLAC

import logging
logging.getLogger(__name__)

def md5(filename):
    logging.debug('plugins.flac.md5( %s )', filename)

    _md5 = None  # Default return value if nothing happens

    try:
        audio_data = audiotools.open(filename).to_pcm()
    except (audiotools.UnsupportedFile, IOError) as err:
        logging.error('Failed to open file %s: %s', filename, err)
    else:
        _md5 = _md5_audio_data(audio_data)

    logging.debug('plugins.flac.md5( %s ) returning: %s', filename, _md5)
    return _md5


def streaminfo_md5(filename):
    logging.debug('plugins.flac.streaminfo_md5( %s )', filename)

    md5 = None

    try:
        audiofile = FLAC(filename)
        # mutagen.flac.FLAC.info() provides access to all content
        # from the STREAMINFO block in flac header.  The docs do not
        # mention md5_signature specifically, but looking at the content
        # of the StreamInfo object returned by the info() method it
        # contains an md5_signature attribute.
        # print( vars( audiofile.info ) )
        # See: http://mutagen.readthedocs.io/en/latest/api/flac.html?highlight=FLAC
        #
        # The value stored in the STEAMINFO block is a 16 byte field hex field.
        # This gets decoded using the format string %02x
        # Zero padding seems to be getting stripped from formatted output,
        # so fixed with an rjust() to zero pad upto the max length of an md5
        # string of 32 characters.
        md5 = ("%02x" % audiofile.info.md5_signature).rjust(32, '0')
    except mutagen.MutagenError as err:
        logging.error('Failed to open file: %s', err)

    logging.debug('plugins.flac.streaminfo_md5( %s ) returning: %s', filename, str(md5))
    return md5


def _md5_audio_data(audio_data):

    hasher = hashlib.md5()

    def update_md5(data):
        hasher.update(data)

    try:
        audiotools.transfer_framelist_data(audio_data, update_md5)
    except (IOError, ValueError) as err:
        logging.error('Failed to _md5_audio_data: %s', err)
        return None
    else:
        return str(hasher.hexdigest())
