#!/usr/bin/env python3.11

import re
import configparser
import sys
import os
import time
from typing import NoReturn
import psutil
from pypresence import Presence

# find a process which matches pattern
# @param pattern - a regex pattern
# @returns - process id if found else None
def find_pid(pattern: str) -> int|None:
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
            cmd = ' '.join(p.cmdline())
            if re.search(pattern, cmd):
                return pid
        except:
            pass
    return None

# parse the proton version of games using it
# @param game - a dict containing the games info
# @returns - proton version if found else None
def get_proton_version(game: dict[str, str]) -> str|None:
    if game['exe'] == '__noauto__':
        return None
    pid = find_pid(f'.*/proton .*{game["exe"]}')
    if not pid or not psutil.pid_exists(pid):
        return None
    try:
        p = psutil.Process(pid)
        for arg in p.cmdline():
            if not re.fullmatch(r'.*/proton', arg):
                continue
            proton_path = re.sub(r'(.*)/proton', r'\1', arg)
            if not os.path.exists((os.path.join(proton_path, 'version'))):
                return None
            with open(os.path.join(proton_path, 'version')) as versionfile:
                return re.sub(r'.* (.*)\n', r'\1', versionfile.read())
    except:
        pass
    return None

# generate option **kwargs for PyPresence based on predefined types
# @param game - a dict containing the games info
# @returns - a dict usable as **kwargs for PyPresence
def gen_options(game: dict[str, str]) -> dict[str, str|int|None]:
    options = dict()
    if game['type'] == 'default':
        options = {'start': int(time.time()),
                   'details': None, 
                   'large_image': f'{game["image"]}', 
                   'large_text': f'{game["pretty"]}', 
                   'small_image': None, 
                   'small_text': None}
    if game['type'] == 'proton':
        options = {'start': int(time.time()),
                   'details': 'via Proton', 
                   'large_image': f'{game["image"]}', 
                   'large_text': f'{game["pretty"]}', 
                   'small_image': 'proton', 
                   'small_text': 'Proton'}
        proton_version = get_proton_version(game)
        if proton_version:
            options['details'] = f'via Proton ({proton_version})'
            options['small_text'] = f'Proton ({proton_version})'

    if game['type'] == 'switch':
        options = {'start': int(time.time()),
                   'details': 'on Nintendo Switch', 
                   'large_image': f'{game["image"]}', 
                   'large_text': f'{game["pretty"]}', 
                   'small_image': 'switch', 
                   'small_text': 'Nintendo Switch'}
    return options

# read the configuration file adding default values where needed
# @returns - a dict containing game-dicts
def read_games_conf() -> dict[str, dict[str, str]]:
    games = dict[str, dict[str, str]]()
    config_path = os.path.join(os.environ.get('XDG_CONFIG_HOME', os.path.join(str(os.environ.get('HOME')), '.config')), 'linux-discord-rpc/games.conf')
    config = configparser.ConfigParser()
    config.read(config_path)
    for game in config.sections():
        info = dict[str, str](config.items(game))
        if 'appid' not in info:
            print(f'Game {game} has no appid configured and will be skipped.')
            break
        if 'image' not in info:
            info['image'] = game
        if 'pretty' not in info:
            info['pretty'] = game
        if 'exe' not in info:
            info['exe'] = '__noauto__'
        if 'type' not in info:
            info['type'] = 'default'
        games[game] = info
    return games

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
    if len(args) < 1:
        print('No option given')
        cli_help()
        exit(1)

    # error if no statefile
    if args[0] != 'help' and not os.path.isfile(statefile):
        print(f'Statefile {statefile} doesn\'t exist.')
        print('Is the daemon running?')
        exit(1)

    if args[0] == 'set':
        if len(args) < 2:
            print(f'{args[0]} requires a game as parameter')
            exit(1)
        state = args[1]
        if state in games:
            with open(statefile, 'w') as f:
                f.write(state)
        else:
            print(f'{state} not a configured game')
            exit(1)

    elif args[0] == 'get':
        with open(statefile) as f:
            print(f.read())

    elif args[0] == 'clear':
        with open(statefile, 'w') as f:
            f.write('')
    
    elif args[0] == 'help':
        cli_help()

    else:
        print(f'Unknown option: {args[0]}')
        exit(1)
    exit(0)

# the main daemon interacting with discord and monitoring
# game processes
def daemon() -> NoReturn:
    games = read_games_conf()
    statefile = os.path.join(os.environ.get('XDG_RUNTIME_DIR', '/tmp'), 'linux-discord-rpc-state')
    try:
        open(statefile, 'w').close()
    except:
        print(f'statefile could not be created at {statefile}')
        exit(1)

    active = None
    rpc = None
    options = None
    firstrun = True
    restorable = False
    while True:
        if firstrun:
            firstrun = False
        else:
            time.sleep(10)

        # wait until discord actually runs
        # and set restorable
        if not find_pid('Discord'):
            print('Discord not running')
            if rpc and options:
                rpc.close()
                restorable = True
            while not find_pid('Discord'):
                time.sleep(1)

        new = None
    
        # first check for manual state
        with open(statefile) as f:
            state = re.sub(r'\n', r'', f.readline())
            for game in games:
                if game == state:
                    new = game

        # then auto state
        if not new:
            for game in games:
                if not games[game]['exe'] == '__noauto__':
                    if find_pid(games[game]['exe']):
                        new = game
        
        # running and not active yet
        if new and new != active:
            print(f'Changing status to {new}')
            if rpc:
                rpc.close()
            try:
                rpc_new = Presence(games[new]['appid'])
                # commit new -> active
                active = new
                rpc = rpc_new
                options = gen_options(games[new])
            except:
                print('Updating status failed. Keeping previous.')
                continue
            finally:
                try:
                    print(options)
                    rpc.connect()
                    rpc.update(**options)
                except:
                    print('Couldn\'t connect to Discord. Retrying.')
                    continue

        # running and already active (restore status)
        elif new and new == active:
            if rpc and options and restorable:
                print(f'Restoring status {active}')
                try:
                    rpc.connect()
                    rpc.update(**options)
                    restorable = False
                except:
                    print('Couldn\'t connect to Discord. Retrying.')
                    continue

        # not running (clear)
        elif not new and active:
            print(f'Clearing status.')
            if rpc:
                rpc.close()
            active = rpc = options = None

        # not running and already cleared
        elif not new and not active:
            pass

# main wrapper around cli and daemon
# calls corresponding function depending on argv[0]
def main(args) -> NoReturn:
    if os.path.basename(args[0]) == 'rpc-cli':
        cli(args[1:])
    elif os.path.basename(args[0]) == 'rpc-daemon':
        daemon()
    else:
        print('This script shouldn\'t be run directly.')
        print('Use a symlink to this file named \"rpc-cli\" or \"rpc-daemon\" instead.')
    exit(0)

if __name__ == '__main__':
    main(sys.argv)

