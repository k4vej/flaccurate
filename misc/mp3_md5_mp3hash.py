# Example showing use of mp3hash library
# pip install mp3hash
# to strip all the header data and shove it through md5
# obtaining an md5 of just the audio data

# FAIL - gives different output for the same mp3 file
# with different header formats!!

import sys
import hashlib
import mp3hash

print( sys.argv[1] )

# init an md5 obj otherwise mp3hash defaults to sha1
md5er = hashlib.md5()

out = mp3hash.mp3hash( sys.argv[1], None, hashlib.md5() )

print( out )
