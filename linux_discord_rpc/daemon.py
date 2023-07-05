import re
import os
import time
from typing import NoReturn
import psutil
from pypresence import Presence

from linux_discord_rpc.procs import find_pid
from linux_discord_rpc.config import read_games_conf

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

if __name__ == '__main__':
    daemon()
