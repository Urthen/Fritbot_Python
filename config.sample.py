# Fritbot configuration file
# Change the configuration settings and rename to config.py in order to run fritbot.

# Twistd application settings
APPLICATION = {
    "name": "fritbot"
}

# Jabber connection settings
JABBER =  {
    "jid": "user@server.name.com/Resource", 
    "password": "password", 
    "server": "server.name.com"
}

# Jabber rooms to join on startup, with per-room nicknames
ROOMS = {
    "Room": "Nickname"
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
}