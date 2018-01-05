flaccurate.py

Why?
Inspired by my obsessive compulsiveness combined with my digital hoarding.  I have a large collection of music, mostly in flac format.  After losing my entire digital collection on several occasions over the years, I slowly refined my archival methods and strategies.  The lessons I have learnt through these losses together with an improved understanding of storage hardware, operating systems and the underlying file systems mean I now have a robust and resilient architecture, with which to store my music collection (and any other files for that matter), for my entire life, without fear of loss of even an individual bit of data corruption.

This strategy centers around a filesystem with “bit rot” protection in the form of data checksumming, namely btrfs.  When used with a RAID 1 mirror, the filesystem is able to detect and automatically correct (or at the very least notify) of any file corruption due to faulty hardware.  Combined with the a double layer of application level checksumming provided by the flac file format (whole file md5sum as well as per frame CRC) - corruption has nowhere to hide.  These features combined with a robust backup scheme == indefinite lossless digital file archival.

flaccurate focuses primarily on the flac file format and its built-in data md5sum.  It will catalogue audio files, recording the md5 of the hash.  On subsequent runs, if it detects any deviation of this hash it will notify you.  For me it is kind of redundant given all of the steps I have outlined above, but it does act as an integrity checker with which to be 100% confident nothing is changing, that you don’t expect to change, over time.

How?


Appendix
Specification for ID3 file format:
http://id3.org

Specification for flac file format:
https://xiph.org/flac/format.html

The Python audio library mutagen is used to accomplish flac metadata parsing:
https://mutagen.readthedocs.io/en/latest/index.html

Spent a lot of time considering python-audio-tools, but is not packaged in Debian repo, and at the time of writing has not been updated since 2015.
http://audiotools.sourceforge.net/index.html
Uploaded to PyPi by a third party contributor (not the original author) under the name of:
fmoo-audiotools (see: https://github.com/tuffy/python-audio-tools/issues/33)
