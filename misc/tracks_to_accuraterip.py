# Example showing use of python audio tools library
# to grab all the pcm data and shove it through md5
# obtaining an md5 of just the audio data

import sys
import glob
import audiotools
import audiotools.accuraterip

tracks = []
for filename in glob.iglob(sys.argv[1] + '**/*.flac', recursive=True):
#    print(filename)
    tracks.append(audiotools.open(filename))

for track in tracks:
    track_meta = track.get_metadata()
#    print(track_meta)

accuraterip_discid = audiotools.accuraterip.DiscID.from_tracks(tracks)
print('AccurateRip Disc ID: %s', accuraterip_discid)

accuraterip_response = audiotools.accuraterip_lookup(tracks)
#print( 'AccurateRip Tracks Lookup Response: %s', accuraterip_response )

accuraterip_response2 = audiotools.accuraterip.perform_lookup(accuraterip_discid)
#print( 'AccurateRip Disc ID Lookup Response: %s', accuraterip_response2 )

for track in accuraterip_response2.keys():
    print('Track', str(track))
    for unique_ar_entry in accuraterip_response2.get(track):
        print( '\tConfidence:', unique_ar_entry[0] )
        print( '\tCRC1:', unique_ar_entry[1], hex(unique_ar_entry[1]).upper().replace('0X','') )
        if( unique_ar_entry[2] != 0 ): print( '\tCRC2:', unique_ar_entry[2], hex(unique_ar_entry[2]).upper().replace('0X','') )

