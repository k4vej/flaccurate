
from .base import Base

import logging
logging.getLogger(__name__)

class NoOp(Base):
    """The noop command does nothing practical for a user.

You probably want to run the selfcheck command which is much more useful.

This exists mostly as a quick high level test, to ensure the system can,
superficially at least, execute the program.
There is something to be said for a quick once over where the python
interpreter loads the top level script, instantiates this command Class and
exits cleanly.  If you see any output (other than this --usage),
then something is probably broken.

Usage:
    cli.py [--usage] noop

For general help:
    cli.py --help
"""

    def __init__(self,args):
        super().__init__(args)

    def run(self):
        return None
