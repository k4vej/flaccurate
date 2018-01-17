import os
import struct
import hashlib
from collections import namedtuple

import logging
logging.getLogger(__name__)
# TODO
# 1.
# Add fallback to search through entire file for ID3
# Inspired by: Perl CPAN module (MPEG::ID3v2Tag)
# http://search.cpan.org/dist/MPEG-ID3v2Tag/lib/MPEG/ID3v2Tag.pm

def md5(filename):
    """Calculate MD5 for an MP3 excluding ID3v1 and ID3v2 tags if
    present. See www.id3.org for tag format specifications."""
    logging.debug('plugins.mp3.md5( %s )', filename)
    _md5 = None

    try:
        mp3_fh = open(filename, "rb")
    except FileNotFoundError:
        logging.error('Failed to open %s: Not found', filename)
        return _md5

    # default starting position is complete file
    audiodata = {
        'start': mp3_fh.tell(),
        'finish': os.stat(filename).st_size,
    }
    logging.debug('plugins.mp3.md5( %s ): Audio range %i-%i bytes', filename, audiodata.get('start'), audiodata.get('finish'))

    logging.debug('plugins.mp3.md5( %s ): Checking for ID3v1 tag', filename)
    if(_id3v1(mp3_fh, audiodata)):
        logging.debug('plugins.mp3.md5( %s ): ID3v1 tag header found - range adjusted %i-%i bytes', filename, audiodata.get('start'), audiodata.get('finish'))
    else:
        logging.debug('plugins.mp3.md5( %s ): No ID3v1 tag found', filename)

    logging.debug('plugins.mp3.md5( %s ): Checking for ID3v1 extended tag', filename)
    if(_id3v1_extended(mp3_fh, audiodata)):
        logging.debug('plugins.mp3.md5( %s ): ID3v1 extended tag header found - range adjusted %i-%i bytes', filename, audiodata.get('start'), audiodata.get('finish'))
    else:
        logging.debug('plugins.mp3.md5( %s ): No ID3v1 extended tag found', filename)

    logging.debug('plugins.mp3.md5( %s ): Checking for ID3v2 tag', filename)
    if(_id3v2(mp3_fh, audiodata)):
        logging.debug('plugins.mp3.md5( %s ): ID3v2 tag found - range adjusted %i-%i bytes', filename, audiodata.get('start'), audiodata.get('finish'))
    else:
        logging.debug('plugins.mp3.md5( %s ): No ID3v2 tag found', filename)

    # Calculate MD5 using stuff between tags
    mp3_fh.seek(audiodata.get('start'))
    _md5 = _md5_audio_data(
        mp3_fh.read(audiodata.get('finish') - audiodata.get('start')))
    mp3_fh.close()

    logging.debug('plugins.mp3.md5( %s ): Returning %s', filename, _md5)
    return _md5


def _md5_audio_data(audio_data):

    hasher = hashlib.md5()
    hasher.update(audio_data)

    return str(hasher.hexdigest())


def _id3v1(mp3_fh, audiodata):
    logging.debug('plugins.mp3._id3v1()')
    has_id3v1 = False

    if(audiodata['finish'] < 128):
        logging.debug(
            'plugins.mp3._id3v1(): File too small to contain ID3v1 tag')
        return has_id3v1

    mp3_fh.seek(-128, 2)  # ID3v1 stored in last 128 bytes
    header = mp3_fh.read(3)
    if(header == "TAG".encode('utf-8')):
        audiodata['finish'] -= 128
        has_id3v1 = True

    return has_id3v1


def _id3v1_extended(mp3_fh, audiodata):
    logging.debug('plugins.mp3._id3v1_extended()')
    has_id3v1_extended = False

    if(audiodata['finish'] < 227):
        logging.debug('plugins.mp3._id3v1_extended(): File too small to contain ID3v1 extended tag')
        return has_id3v1_extended

    # ID3v1 extended stored in 227 bytes before 128 byte ID3v1 tag:
    # 335 bytes from end of file
    mp3_fh.seek(-335, 2)
    header = mp3_fh.read(4)
    if(header == "TAG+".encode('utf-8')):
        audiodata['finish'] -= 227
        has_id3v1_extended = True

    return has_id3v1_extended


def _id3v2(mp3_fh, audiodata):
    logging.debug('plugins.mp3._id3v2()')
    has_id3v2 = False

    if(audiodata.get('finish') < 10):
        logging.debug('plugins.mp3._id3v2(): File too small to contain ID3v2 tag')
        return has_id3v2

    mp3_fh.seek(0)  # ID3v2 tag header is in first 10 bytes
    # ID3v2 header (see: http://id3.org/id3v2.4.0-structure)
    # 10 bytes as follows:
    # bytes content
    # 3     ID3
    # 2     version
    # 1     flags
    # 4     tag size (Synchsafe integer)
    id3v2_header_template = namedtuple('id3v2_header_template', 'id3 majorver minorver flags tagsize_synchsafe')
    id3v2_struct_format = '!3s2BBI'  # !: No padding is added when using non-native size and alignment
    id3v2_struct_format_size = struct.calcsize(id3v2_struct_format)
    #logging.debug('plugins.mp3.md5(): Calculated size of binary unpacking struct (%s) as: %i', id3v2_struct_format, id3v2_struct_format_size)

    header = id3v2_header_template._make(struct.unpack(id3v2_struct_format, mp3_fh.read(id3v2_struct_format_size)))
    #print(header)

    if(header.id3 == "ID3".encode('utf-8')):
        has_id3v2 = True
        ID3v2 = 'ID3v2.' + str(header.majorver)
        #logging.debug('plugins.mp3._id3v2(): Version %s found', ID3v2)

        tagsize = unsynchsafe( header.tagsize_synchsafe )
        #logging.debug('plugins.mp3.md5(): %s body size %s bytes', ID3v2, str(tagsize))

        # Flat bit 4 means footer is present (10 bytes)
        footer = header.flags & (1 << 4)
        if footer:
            #logging.debug('plugins.mp3._id3v2(): %s footer found +10 bytes', ID3v2)
            tagsize += 10

        # Seek to end of ID3v2 tag
        mp3_fh.seek(tagsize, 1)

        # fh current position should now be after all ID3v2 metadata
        audiodata['start'] = mp3_fh.tell()

    return has_id3v2

def unsynchsafe(num):
    # Source: https://stuffivelearned.org/doku.php?id=misc:synchsafe
    out = 0
    mask = 0x7f000000
    for i in range(4):
        out >>= 1
        out |= num & mask
        mask >>= 8
    return out
