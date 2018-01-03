from mutagen.flac import FLAC

testfile = './test/test-data/01 - Mars, the Bringer of War.flac'

def get_flac_md5( filename ):
  audiofile = FLAC( filename )
  #print( audiofile )
  print( vars( audiofile.info) )

  #audiofile_streaminfo = audiofile.StreamInfo
#  audiofile.pprint()

get_flac_md5( testfile ) 
