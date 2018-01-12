import logging
logging.getLogger(__name__)

import os
import binascii
import struct
import hashlib
from collections import namedtuple
from struct import *
from mutagen.id3 import ID3

#TODO
# 1.
# Add fallback to search through entire file for ID3
# Inspired by: Perl CPAN module (MPEG::ID3v2Tag)
# http://search.cpan.org/dist/MPEG-ID3v2Tag/lib/MPEG/ID3v2Tag.pm
#
# 2.
# Slurp mp3 header tag size into an array so it doesn't
# need storing and processing as individual vars
#
def md5( filename ):
    """Calculate MD5 for an MP3 excluding ID3v1 and ID3v2 tags if                                                                                      
    present. See www.id3.org for tag format specifications."""                                                                                         
    logging.debug('get_mp3_md5_signature( %s )', filename)
    md5 = None

    try:
        f = open(filename, "rb")
    except FileNotFoundError:
        logging.error('Failed to open %s: Not found', filename)
        return md5

    start = f.tell()
    finish = os.stat(filename).st_size;
    logging.debug('Audio data range set to %i-%i bytes', start, finish)

    logging.debug('Checking for ID3v1 tag')
    f.seek(-128, 2) # ID3v1 stored in last 128 bytes
    header = f.read(3)
    if( header == "TAG".encode('utf-8') ):
        finish -= 128
        logging.debug('ID3v1 tag header found: Audio data range updated %i-%i bytes', start, finish)
    else:
        logging.debug('No ID3v1 tag found')

    logging.debug('Checking for ID3v2 tag')
    f.seek(0)
    #id3v2_header_template = namedtuple('id3v2_header_template', 'id3 majorver minorver flags ss1 ss2 ss3 ss4')
    id3v2_header_template = namedtuple('id3v2_header_template', 'id3 majorver minorver flags ss1 ss2 ss3 ss4')
    # ID3v2 header (see: http://id3.org/id3v2.4.0-structure)
    # 10 bytes as follows:
    # bytes content
    # 3     ID3
    # 2     version
    # 1     flags
    # 4     tag size (Synchsafe integer)
    id3v2_struct_format = '!3s2BBBBBB' # !: No padding is added when using non-native size and alignment
    id3v2_struct_format_size = calcsize(id3v2_struct_format)

    logging.debug('Calculated size of binary unpacking struct (%s) as: %i', id3v2_struct_format, id3v2_struct_format_size)

    header = id3v2_header_template._make(struct.unpack(id3v2_struct_format, f.read(id3v2_struct_format_size)))
    #print(header)

    if( header.id3 == "ID3".encode('utf-8')):
        ID3v2 = 'ID3v2.' + str(header.majorver)
        # Flat bit 4 means footer is present (10 bytes)                                                                                                
        footer = header.flags & (1<<4)                                                                                                                        
        tagsize = (header.ss1<<21) + (header.ss2<<14) + (header.ss3<<7) + header.ss4                                                                                    
        #logging.debug(ID3v2 + ' body size ' + str(tagsize) + ' bytes')
        # Seek to end of ID3v2 tag                                                                                                                     
        f.seek(tagsize, 1)                                                                                                                            
        
        if footer:
            logging.debug(ID3v2 + ' footer found additional 10 bytes')
            f.seek(10, 1) # footer found progress fh position                                                                                                                          
        # fh current position should now be after all ID3v2 metadata
        start = f.tell()                                                                                                                               
        logging.debug(ID3v2 + ' tag header found: Audio data range adjusted %i-%i bytes', start, finish)
    else:
        logging.debug('No ID3v2 tag found')
    
    # Calculate MD5 using stuff between tags                                                                                                           
    f.seek(start)
    h = hashlib.md5()
    h.update(f.read(finish-start))                                                                                                                     
    f.close()

    md5 = str(h.hexdigest())
    logging.debug('get_mp3_md5_signature( %s ) returning: %s', filename, md5)
    return md5
