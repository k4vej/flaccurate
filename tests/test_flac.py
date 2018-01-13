import pytest
import plugins.flac


def test_invalid():
    assert(plugins.flac.md5('moo') == None)


@pytest.mark.parametrize( "input_file, output_md5", [
        ('tests/test-data/good-data/flac/01 - Mars, the Bringer of War.flac',
          '7828ad7e6a08d9e9fc4264e0c0db48db'),
        ('tests/test-data/good-data/flac/02 - Venus, the Bringer of Peace.flac',
          '071e0893b187bf7f9e3ad6e14fc7e589'),
        ('tests/test-data/good-data/flac/03 - Mercury, the Winged Messenger.flac',
          'e85f01270c0fe56929c9f74551a0ff5b'),
        ('tests/test-data/good-data/flac/04 - Jupiter, the Bringer of Jollity.flac',
         '03b135cb00092e1fb80bb882783f4426'),
        ('tests/test-data/good-data/flac/05 - Saturn, the Bringer of Old Age.flac',
         '0883b29698ad525feebe998dec9b0c0b'),
        ('tests/test-data/good-data/flac/06 - Uranus, the Magician.flac',
         '8943845f55ba1aa153dc35012a28aed0'),
        ('tests/test-data/good-data/flac/07 - Neptune, the Mystic.flac',
         '48c251e59a08a7f6b4882890f285ec13'),
    ]
)
def test_valid(input_file, output_md5):
    assert(plugins.flac.md5(input_file) == output_md5)
