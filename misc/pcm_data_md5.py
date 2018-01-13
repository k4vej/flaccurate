# Example showing use of python audio tools library
# to grab all the pcm data and shove it through md5
# obtaining an md5 of just the audio data

import sys
import hashlib
import audiotools

def update_md5( data ):
    md5er.update(data)

# open input file from argument 1
pcm_data = audiotools.open(sys.argv[1]).to_pcm()

# init an md5 obj
md5er = hashlib.md5()

# pass all the raw pcm audio data to the update_md5() func
audiotools.transfer_framelist_data(pcm_data,update_md5)

pcm_data.close()
print( str(md5er.hexdigest()) )
