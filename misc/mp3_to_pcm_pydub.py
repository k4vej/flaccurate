import sys
from pydub import AudioSegment

sound = AudioSegment.from_mp3(sys.argv[1])

# sound._data is a bytestring
raw_data = sound._data

print(raw_data)
