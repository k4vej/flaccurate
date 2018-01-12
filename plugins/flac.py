import logging
logging.getLogger(__name__)


def streaminfo_md5( filename ):
    import mutagen
    from mutagen.flac import FLAC

    logging.debug('plugins.flac.streaminfo_md5( %s )', filename)
    md5 = None
    try:
        audiofile = FLAC( filename )
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
        md5 = ( "%02x" % audiofile.info.md5_signature ).rjust(32,'0')
    except mutagen.MutagenError as err:
        logging.error( 'Failed to open file: %s', err )

    logging.debug('plugins.flac.streaminfo_md5( %s ) returning: %s', filename, str(md5))
    return md5

def md5( filename ):
    import hashlib
    import audiotools

    logging.debug('plugins.flac.md5( %s )', filename)
    md5 = None

    def update_md5( data ):
        md5er.update(data)

    md5er = hashlib.md5()

    try:
        pcm_data = audiotools.open(filename).to_pcm()
        audiotools.transfer_framelist_data(pcm_data,update_md5)
        pcm_data.close()
        md5 = str(md5er.hexdigest())
    except audiotools.UnsupportedFile as err:
        logging.error( 'Failed to open file: %s', err )

    logging.debug('plugins.flac.md5( %s ) returning: %s', filename, md5)
    return md5
