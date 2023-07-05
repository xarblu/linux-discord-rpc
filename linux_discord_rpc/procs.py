import os
import psutil
import re

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
