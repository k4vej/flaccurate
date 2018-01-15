flaccurate.py

What?

flaccurate records an md5 checksum of the audio data portion of your music collection.  During the next run, it will recalculate the checksum, highlighting any deviation from previous records.  It is basically what flac provides baked in, but on steroids.  In short it helps keep your lossless audio, lossless.  The audio data only portion is particularly relevant, as this is what we need to keep unmodified - tags and other transient information is considered superfluous and does not contribute towards the objective of lossless audio.

Although flaccurate was originally designed to cater for flac files only, I succumbed to peer pressure and relented to a need to support other (inferior) file formats, on grounds of "the diverse nature of any good music collection" or something to that effect.  To that end, flaccurate is written based on a plugin system, which in theory allows arbitrary file types, supported through the presence of a corresponding plugin (See Appendix: Supported File Formats),

flaccurate assumes the source data on its first run is perfect.  For flac files it is possible to verify this assumption checking the decoded audio data checksum against the recorded md5 baked into the file format (See Appendix: FLAC), for other file formats like mp3 this is not possible.  This clever feature of flac removes the need to write out the checksum to a database for future verification, for flac files at least.  However, there are many reasons why a separate record of the checksum data is a good idea:
1. Convenience - storing and referencing the checksum data all in one place is a lot easier than trawling through individual files manually.
2. Other file formats - don't have the same clever integrity features baked into their format or tooling.  flaccurate provides this same integrity checking feature for every supported file format.
3. Paranoia - there is nothing to stop the header containing the checksum itself becoming corrupt, leading to a false positive - suggesting the audio portion of the file is corrupt, when in fact it is simply the metadata in the header.  Unlikely - but not impossible.  flaccurate provides an external analysis tool, using checksum records stored in a database, separate and distinct from the source files it catalogues.  As a further layer of paranoia, flaccurate also maintains a checksum of the complete database, which is calculated and verified before use (a feature I like to call: checksum introspection).

How?

High level operational algorithm:
	For each supported file type (read: plugin)
    	For each matching file found
			Calculate the audio md5 checksum 
				If the database record exists for file 
					Compare new checksum against database record
						If checksum matches all good
						If checksum doesn't match report it
				If the database has no record for file - insert it for first time 

Why?
I am a digital hoarder, with a digital collection of music >1TB in size, mostly in flac format.  I have OCD aspirations for curating and maintaining this music collection.  I have lost my entire digital collection on several occasions over the years.  This hard won lesson, together with an improved understanding of storage hardware, operating systems and underlying file systems have helped forge my current archival methods and strategies.  I now have a resilient architecture with which to store my music collection (and any other files for that matter), for my entire life, without fear of data loss, of even an individual bit.

This strategy centers around a filesystem with data checksumming (See Appendix: BTRFS) to protect against “bit rot” and storage medium failings in the form of expected uncorrectable read errors.  In a mirrored RAID configuration, the filesystem is able to detect and automatically correct (or at the very least notify) of any file corruption.  Combined with the a double layer of application level checksumming provided by the flac file format - corruption has nowhere to hide (See Appendix: FLAC).  These features combined with a robust backup scheme is about as good as it gets for indefinite lossless digital file archival.

Personally, the main feature of flaccurate is kind of redundant given all of the steps I have outlined above, but it does act as an integrity checker with which to be 100% confident nothing is changing over time.  To that end I would recommend running a verification once a month;  Specifically, run it before overwriting any known good backup copy you may have of your music files.


Appendix: Supported File Formats
flaccurate processes supported file types using a plugin system (See folder plugins/ in source).  Each plugin is a python module with the same filename as the extension it provides support for.  At the time of writing these include:
 - flac 
 - mp3

The plugins derive from the abstract base class: abc.py - which dictates the mandatory interface that needs to be implemented for flaccurate to utilise each plugin in the same manner.  At the time of writing this is simply a function called md5( filename ).

Appendix: FLAC
Not one but two layers of application level data integrity checking.  An md5 checksum of the decoded audio data is stored in the header for overall audio integrity verification as well as per frame CRC (See https://xiph.org/flac/format.html)
 
Verify the integrity of the decoded audio data stored in a flac file against its md5 checksum header:
flac -t filename.flac

Display the md5 checksum stored in the header:
metaflac --show-md5sum filename.flac

Appendix: BTRFS
Hailed as the next generation linux filesystem.  It has a feature which is few and far between (especially in Microsoft land), which is - data checksumming;  Providing data integrity checking baked into the filesystem layer.  It has the capability to detect (and automatically correct in mirrored RAID) any file corruption during read operations.

Appendix: Reference material
Specification for ID3 file format:
http://id3.org

Specification for flac file format:
https://xiph.org/flac/format.html

The Python audio library mutagen is used to accomplish flac metadata parsing:
https://mutagen.readthedocs.io/en/latest/index.html

Another Python audio library python audio tools is used for its flac to PCM functions.  Its packaging does not reflect the maturity of the library itself.  It is not packaged in Debian repo, and at the time of writing has not been updated since 2015.
http://audiotools.sourceforge.net/index.html
Uploaded to PyPi by a third party contributor (not the original author) under the name of:
fmoo-audiotools (see: https://github.com/tuffy/python-audio-tools/issues/33)

TODO
- Add accuraterip support
- Possibly add abstract base class from which plugins derive their interface?
