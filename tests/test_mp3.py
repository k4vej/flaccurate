import pytest
import plugins.mp3


def test_invalid():
    assert(plugins.mp3.md5('moo') == None)


@pytest.mark.parametrize("input_file, output_md5", [
     ('tests/test-data/good-data/mp3/id3v1.mp3',
      '8d2772f663ce6cd424a36b37cc6d9c5f'),
     ('tests/test-data/good-data/mp3/id3v1_empty.mp3',
      '8d2772f663ce6cd424a36b37cc6d9c5f'),
     ('tests/test-data/good-data/mp3/id3v1_id3v24.mp3',
      '8d2772f663ce6cd424a36b37cc6d9c5f'),
     ('tests/test-data/good-data/mp3/id3v23.mp3',
      '8d2772f663ce6cd424a36b37cc6d9c5f'),
     ('tests/test-data/good-data/mp3/id3v23_empty.mp3',
      '8d2772f663ce6cd424a36b37cc6d9c5f'),
     ('tests/test-data/good-data/mp3/id3v24.mp3',
      '8d2772f663ce6cd424a36b37cc6d9c5f'),
     ('tests/test-data/good-data/mp3/id3v24_empty.mp3',
      '8d2772f663ce6cd424a36b37cc6d9c5f'),
     ]
)
def test_valid(input_file, output_md5):
    assert(plugins.mp3.md5(input_file) == output_md5)
