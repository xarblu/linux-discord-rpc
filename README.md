# linux-discord-rpc
Custom Discord Rich Presence for Linux

## Dependencies
`python3` (tested with 3.11)  
`pypresence` [pypi](https://pypi.org/project/pypresence/)  
`psutil` [pypi](https://pypi.org/project/psutil/)  
`pip` or `pipx` (manual install only, `pipx` recommended)

## Installation
### A) Package  
If you're using Gentoo Linux you can install this from my overlay:  
`# eselect repository enable xarblu-overlay`  
`# emerge net-misc/linux-discord-rpc`  

### B) Manual Install  
Install via pipx:
`$ pipx install https://github.com/xarblu/linux-discord-rpc.git`  

Install via pip:  
`$ pip install --user https://github.com/xarblu/linux-discord-rpc.git`  

Optionally install the systemd-service (you may need to adjust the `ExecStart=` line)  
`$ wget https://raw.githubusercontent.com/xarblu/linux-discord-rpc/main/extra/linux-discord-rpc.service -O ~/.config/systemd/user/linux-discord-rpc.service`  

## Behaviour/Usage
Should be called via the aforementioned symlinks.  
`rpc-daemon` is the daemon handling game detection and the communication with Discord  
`rpc-cli` is a simple cli to set/get/clear a configured game manually  

## Configuration
### Main Config
Configuration is done under `$XDG_CONFIG_HOME/linux-discord-rpc/games.conf` and (currently) uses
ini syntax (this might get changed to toml because ini is somewhat funky with case-sesitive strings).  

A config looks like this:
```
## each section corresponds to a game
## this is what you would use with "rpc-cli set <game>" 
## required
# [game]

## discord application id to use for this game
## required get this at https://discord.com/developers/applications
# appid =

## image to use for this game
## optional - defaults to section name
# image =

## pretty name
## optional - defaults to section name
# pretty = 

## name of the games executable to search for auto detection
## optional - if unset don't do auto detection
# exe = 

## selecting a type gives extra info in your rich presence
## one of {default, proton, switch}
## optional - falls back to default
# type = 
```
### The Discord Side
For a proper config you need to setup applications in [discords developer portal](https://discord.com/developers/applications).  
There create a new application, give it a name and copy the application id to your config.  
The next step is image ressources. Add those under Rich Presence -> Art Assets.  
If you use a `type` that isn't `default` setting you should have an image corresponding  
to that type uploaded (it will be used as an indicator).
