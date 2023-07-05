import time

from linux_discord_rpc.procs import get_proton_version

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
