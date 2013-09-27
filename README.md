FritBot - The Angriest Bot
==========================

Introduction
------------

FritBot is a bot designed, in theory, to be a largely service-independent, modularly expandable chat bot. In reality, he mostly just yells at you and breaks things. Use with caution.

License
-------

This software is licensed under the terms of the `LICENSE` file (Apache License, Version 2.0). Please read this file for legal license text.

Installation & Setup
--------------------

Prerequisites: Before starting, you should have installed virtualenv and virtualenvwrapper with `pip install virtualenv virtualenvwrapper` if you don't have them already. They are awesome and you will love them. Additionally,
you must install mongodb (v1.6+ required, 2.2+ preferred) as platform appropriate.

1. Check out the repo! Yay! If you want to make updates to fritbot itself, fork the repo and check out your own copy, then open pull requests.
2. Make a virtual environment for fritbot with `mkvirtualenv fb`. You can leave this virtual environment with `deactivate` and get back in later with `workon fb`. Read the virtualenvwrapper documentation for more info.
3. Install requirements with `pip install -r requirements.txt` (Note: If you have problems installing pyOpenSSL on an ubuntu machine, run `apt-get install libssl-dev` first)
4. You will need to add your own config .yaml file to overwrite the defaults. See `default.yaml` for all available options. `.gitignore` automatically ignores files that look like `my*.yaml` so name it something like `my_config.yaml` to make sure you never check it in by accident. Don't expose your passwords! For more information, see the configuration section below.
5. Run mongodb however is appropriate
6. Run the bot with `twistd -n fritbot my_config.yaml` to start in daemonzied mode: All output will be logged to the console, useful for debugging. Press ctrl-c to exit.
7. If you would like to run a more permanent instance, remove the `-n` option. Output will be logged to file and the bot must be shut down via a shutdown command from chat or kill command from the console.

Configuration
-------------

Configuration is done through layered YAML files. This means if you have configurations that may want to inherit - for example, a normal connection config and a minor tweak for testing, as I have - you can split them up into two YAML files and specify them both on the commandline. The later files will take precedence whenever there is a conflict. Here's what I normally run when testing: `twistd -n fritbot my_jabber.yaml testbot.yaml`

See `default.yaml` for more information about configuration: each section and option should be well documented.

Creating a Module
-----------------

First, you'll want to take a look at the hello module in `fb/modules/hello.py`. It showcases the most basic capability of the bot: Responding to commands given to the bot and things said in the chat room. Modules are basically simple classes extending from the base module class and consist of a bit of metadata information (Used by the online help system) and an initialization function. The initialization function defines one or more commands or listeners. Commands are things said to the bot and must be prefaced with the bot's configurable name, and usually are more directive. They can also include arguments, such as `fritbot quote bob`. Listeners look for anything said in any room the bot is in, but cannot take arguments and usually should be used sparingly to avoid being spammy.

To start creating a module, start off by copying `fb/modules/_boilerplate.py` and renaming it to something appropriate. Rename the class inside, `MyModule`, as well; then make sure to change the `module = MyModule` line at the bottom to reflect the new name. You'll notice that the boilerplate module class has several attributes already defined:

* `uid`: A unique identifier for the class, which must match the filename you saved it as.
* `name`: A nice name for the module, displayed in Help.
* `description`: A short description for the module.
* `author`: Your name and, if desired, email address.
* `children`: Child modules. If you are not building a supermodule (see the section on Supermodules below) you can erase this line.
* `commands`: Dictionary of commands. If you are not using commands, remove this code.
* `listeners`: Dictionary of listeners. If you are not using listeners, remove this code.
* `apis`: Dictionary of endpoints to add to the API. If you have none, remove this code.

Once the module's attribtues are set up, you can start adding Commands, Listeners, and APIs. 

Creating Commands
-----------------

Commands must be said directly to the bot in a one-on-one conversation, or addressed to the bot with one of it's nicknames, for example `fritbot say hello`. Commands are the most common functionality as it must be explicitly triggered. Anything you can do with Python, you can do with a command! In their simplest form, the command will simply return a string that represents the response intended to be sent back, either to the user (if triggered in a one-on-one) or to the room. However, you can send any amount of messages to any user or the room as part of a command, or return no message at all - though that tends to get confusing to see if something actually happened!

To register a very simple command like the one in the next example, all you really need is the following:

	commands = {
		"hello": {
			"keywords": "say ((hello)|(hi))",
			"function": "sayHello",
			"name": "Say Hello",
			"description": "Says Hello to the user"
		}
	}

Commands (And listeners) take the following arguments:

* `keywords`: Regex, or list of regexes, that can trigger this command. Any valid regex is possible here.
* `function`: Function (on the Module's class) to execute which takes the argument pattern explained below
* `name`: Name of the function, used in help.
* `description`: Description of the command, stating usage and expected functionality.

The most simple command is below:

	@response
	def sayHello(self, bot, room, user, args):
		return "Hello, " + user['nick']
	
`@response` is a python decorator indicating that this function is a bot response; this wraps it in some logic that will allow the bot to automatically respond with the functions' return value no matter where the input came from. Other decorators available, which should be placed before `@response`, are `@admin`, which verifies that the user is an administrator, `@room_only` which will restrict access to the function to rooms only, and `@user_only` which will restrict access to only private chats to the bot. These can be used in combination.

The function itself takes four arguments: `bot` which is the actual FritBot class instance, `room` which is the Room object that the command was triggered in or `null` if it was a private chat, `user` which is the User object who triggered the function, and `args` which is either the arguments parsed from the command, or the match object of the regex in a listener. To actually cause the bot to respond to commands or listeners, simply have it return a string or unicode value. What happens in between the two is completely up to you - anything possible in python can be done.

Creating Listeners
------------------

Listeners are created and function almost exactly the same way as commands, except they do not have to be intended for the bot. Instead, Fritbot listens to all messages and checks to see if they match the listener's regex. If it does, the function executes with the regex match object as `args`.

Creating API Endpoints
----------------------

Each module can have one or more API endpoints, so long as they do not conflict with other loaded modules.

Documentation TODO, but in the meantime, you can check out `apitest` or `apimessage` for simple examples how this works.

Creating Supermodules
---------------------

Supermodules are effectively a bundle of modules, for the purpose of keeping individual module files smaller. A supermodule is installed or uninstalled as a whole, though individual sub-modules can fail while letting other sub-modules load successfully.

Instead of creating a single file in the `modules` directory, to start a supermodule instead create a folder. In the folder you must add an `__init__.py` file. This file acts as the "parent" module and functions completely normally. Other sub-modules, residing in the same folder, also otherwise act entirely normally. To link it all together, import the sub-modules from the parent module, and add the modules to the `children` attribute of the parent module. See `supermodule_example` for a clean example of how to create a simple supermodule with two sub-modules.
