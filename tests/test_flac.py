import pytest
from flac import Flac

def test_instance():
    myFlac = Flac('moo')
    assert( isinstance( myFlac, Flac ) )
