import sys
import os

from typing import NoReturn

from linux_discord_rpc.config import read_games_conf

# cli help
def cli_help() -> None:
    print('Usage: rpc-cli [set <game>]|[get]|[clear]|[help]')
    print('         set   - sets <game> as the status')
    print('         get   - print currently set game')
    print('         clear - clears game status')
    print('         help  - print this help')

# cli to interact with the manual state file
# @param args - list of argument strings
def cli(args: list[str]) -> NoReturn:
    games = read_games_conf()
    statefile = os.path.join(os.environ.get('XDG_RUNTIME_DIR', '/tmp'), 'linux-discord-rpc-state')
    if len(args) < 2:
        print('No option given')
        cli_help()
        exit(1)

    # error if no statefile
    if args[1] != 'help' and not os.path.isfile(statefile):
        print(f'Statefile {statefile} doesn\'t exist.')
        print('Is the daemon running?')
        exit(1)

    if args[1] == 'set':
        if len(args) < 3:
            print(f'{args[1]} requires a game as parameter')
            exit(1)
        state = args[2]
        if state in games:
            with open(statefile, 'w') as f:
                f.write(state)
        else:
            print(f'{state} not a configured game')
            exit(1)

    elif args[1] == 'get':
        with open(statefile) as f:
            print(f.read())

    elif args[1] == 'clear':
        with open(statefile, 'w') as f:
            f.write('')
    
    elif args[1] == 'help':
        cli_help()

    else:
        print(f'Unknown option: {args[1]}')
        exit(1)
    exit(0)

if __name__ == '__main__':
    cli(sys.argv)

