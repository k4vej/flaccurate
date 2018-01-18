# Avoid module and class double-barrelled importing by
# importing the Classes in __init__.py so the point of use can simply be:
# import Class
from .database import Database
import flaccurate.plugins
