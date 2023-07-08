import sys

from linux_discord_rpc import (cli, daemon)

def run_cli():
    cli.cli(sys.argv)

def run_daemon():
    daemon.daemon()

if __name__ == '__main__':
    print("WARN: Called via module. Use rpc-cli/rpc-daemon entry points instead.")
    if len(sys.argv) < 2 or sys.argv[1] not in ['cli', 'daemon']:
        print("Module call requires one of [cli, daemon] as first argument.")
        exit(1)

    if sys.argv[1] == 'cli':
        sys.argv = sys.argv[1:]
        run_cli()
    elif sys.argv[1] == 'daemon':
        run_daemon()
