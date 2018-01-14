# Example showing use of filetyp library

import sys
import filetype

# open input file from argument 1
print(filetype.match(sys.argv[1]) )

f = open( sys.argv[1], 'rb' )

buf = f.read( 256 )
print(filetype.get_type(None,'flac').match( buf ))
