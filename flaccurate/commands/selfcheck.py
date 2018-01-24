from .base import Base

import logging
logging.getLogger(__name__)

class SelfCheck(Base):
    """The selfcheck command performs some validation on the flaccurate environment then exits.

The validation consists of loading the database if it exists, or creating it if not.
It then perfoms a database integrity check, and finally verifies the database checksum
to ensure it has not changed since our last recorded change.

Usage:
    flaccurate.py [--usage] selfcheck

For general help:
    flaccurate.py --help
"""
    def __init__(self,args):
        super().__init__(args)

    def run(self):
        logging.info('Self check starting')

        self.db = self._init_database()
        self.plugins = self._init_plugins()

        logging.info('Self check complete - exiting...')
