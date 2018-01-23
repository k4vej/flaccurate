import sys

import logging
logging.getLogger(__name__)

class Plugins():
    """The plugin loader class.

On instantiation will enumerate all the plugins available.
"""
    PLUGINS_PATH = 'plugins'

    def __init__(self, args):
        self.args = args
        self.debug = self.args.debug
        self.silent = self.args.silent
        self.quiet = self.args.quiet
        logging.debug('Plugins __init__ %s', vars(self.args))
        
        self.plugins = self._init_plugins()
        logging.info('Plugins available: %s', ', '.join(self.supported_filetypes()))

    def _init_plugins(self):
        logging.debug('_init_plugins( %s )', self.PLUGINS_PATH)
        plugins = self._discover_plugins()

        for plugin in plugins.keys():
            logging.debug('Plugin found: %s', plugin)
        
        return plugins

    def _discover_plugins(self):
        return {module_name.replace('flaccurate.plugins.',''): sys.modules[module_name]
                    for module_name in sys.modules.keys()
                        if( self._valid_plugin(module_name))}

    def _valid_plugin(self,module_name):
        if( module_name.startswith( 'flaccurate.plugins.' ) ):
            return True
        else:
            return False

    def supported_filetypes(self):
        return self.plugins.keys()

    def plugin(self,filetype):
        return self.plugins.get(filetype, None)
