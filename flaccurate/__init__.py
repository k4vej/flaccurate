# Avoid module and class double-barrelled importing by
# importing the Classes in __init__.py so the point of use can simply be:
# import Class
from flaccurate.database import Database
from flaccurate.exception import Usage
import flaccurate.plugins
