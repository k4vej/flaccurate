import sys
import argparse

from inspect import getmembers, isclass

def main():
    """Main CLI entrypoint."""
    import flaccurate.commands
    import flaccurate
    args = _init_argparse()

    # Here we'll try to dynamically match the command the user is trying to run
    # with a pre-defined command class we've already created.
    # Source: https://github.com/rdegges/skele-cli
    for user_command in args.command:
        if hasattr(flaccurate.commands, user_command):
            module = getattr(flaccurate.commands, user_command)
            flaccurate.commands = getmembers(module, isclass) # get class name
            command = [command[1] for command in flaccurate.commands if command[0] != 'Base'][0]
            try:
                command = command(args) # instantiate
            except flaccurate.Usage as e:
                print(e)
            else:
                command.run()

def _init_argparse():
    # obtain list of commands found in flaccurate.commands module namespace
    available_commands = _discover_commands()

    # Use this enumerated list of available_commands to populate argparse
    # choices for the mandatory "command" positional parameter - and infom
    # users of the available choices by printing them in the epilog for the
    # help output.  This is done rather than statically populating the parser
    # with sub-command help, as the point of the commands is their creation
    # and presence are dynamically discovered at runtime.
    epilog_text = 'commands available: ' + ', '.join(available_commands)
    parser = argparse.ArgumentParser(epilog=epilog_text)

    # Most defaults are explicitly set to None
    # Setting fallback defaults is instead delayed until after
    # argparse is complete so that:
    # 1. We can detect and explicitly log this behaviour
    # 2. Make more complex decisions about what the default should be
    parser.add_argument(
        '--debug',
        help='enable debug', action='store_true'
    )
    parser.add_argument(
        '--quiet',
        help='quiet mode - will only output warnings or errors', action='store_true'
    )
    parser.add_argument(
        '--silent',
        help='silent mode - will output nothing', action='store_true'
    )
    parser.add_argument(
        '--usage',
        help='provide command specific usage guidance', action='store_true'
    )
    parser.add_argument(
        '--force',
        help='force through actions - ignoring warnings accepting implicit defaults', action='store_true'
    )
    parser.add_argument(
        '--input',
        nargs='?',
        type=str,
        default=None,
        help='specify directory where audio files are stored'
    )
    parser.add_argument(
        '--database',
        nargs='?',
        type=str,
        default=None,
        help='specify the database file to use',
    )
    parser.add_argument(
        'command',
        nargs='*',
        type=str,
        help='run this command',
        metavar='command',
        choices=_discover_commands()
    )
    return parser.parse_args()

def _discover_commands():
    discovered_commands = []
    for module_name, imported_module in sys.modules.items():
        if(module_name.startswith('flaccurate.commands.')):
            command_name = module_name.replace('flaccurate.commands.','')
            if(command_name != 'base'):
                discovered_commands.append(command_name)
    return discovered_commands

if __name__ == '__main__':
    main()
