import configparser
import os

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
