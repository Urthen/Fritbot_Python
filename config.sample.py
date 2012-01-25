# Fritbot configuration file
# Change the configuration settings and rename to config.py in order to run fritbot.

# Twistd application settings
APPLICATION = {
    "name": "fritbot"
    "modules": ['core', 'hello']
}

# API Settings, comment entire section out to disable the API.
API = {
    "debug": True, # If set to True, will display a rich error message instead of a default json error message when server errors occur.
    "default_limit": 100,
    "port": 4886,
    "login_timeout": 5 # minutes until login token expires
}

# Jabber connection settings
JABBER =  {
    "jid": "user", # as in, user@server.name.com/Resource
    "resource": "resource",
    "password": "password", 
    "server": "server.name.com"
}

# Jabber rooms to join on startup, with per-room nicknames
ROOMS = {
    "Room": "Nickname"
}

CONFLUENCE = {
    "enabled": False,
#    "url": "https://www.example.com/confluence/rpc/xmlrpc",
#    "username": "username",
#    "password": "password"
}

# Logging settings
LOG = {
    "filename": APPLICATION["name"] + ".log",
    "directory": "logs",
    "traffic": True # Do we want to log all XMPP traffic?
}

# MongoDB settings
DB = {
    "name": "fritbot"
}

# Other settings
CONFIG = {
    "name": "FritBot", #primary nickname
    #also accepted usages. Case insensitive for the actual usage, but here they must be lowercase and should not contain punctuation.
    "nicknames": ["fb"],
    "status": "Angriest Bot Ever", # Status message
    "refresh": 1, # Minimum refresh time, in seconds.
    "racy": False, #Whether or not to include racy/NSFW content in searches
}