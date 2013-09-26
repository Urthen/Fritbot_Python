FritBot - The Angriest Bot
==========================

Introduction
------------

FritBot is a bot designed, in theory, to be a largely service-independent, modularly expandable chat bot. In reality, he mostly just yells at you and breaks things. Use with caution.

Installation & Setup
--------------------

Prerequisites: Before starting, you should have installed virtualenv and virtualenvwrapper with `pip install virtualenv virtualenvwrapper` if you don't have them already. They are awesome and you will love them. Additionally,
you should install mongodb (v1.6+ required, 2.2+ preferred) as platform appropriate.

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

Creating a module
-----------------

First, you'll want to take a look at the hello module in `fb/modules/hello.py`. It showcases the most basic capability of the bot: Responding to commands given to the bot and things said in the chat room. Modules are basically simple classes extending from the base module class and consist of a bit of metadata information (Used by the online help system) and an initialization function. The initialization function defines one or more commands or listeners. Commands are things said to the bot and must be prefaced with the bot's configurable name, and usually are more directive. They can also include arguments, such as `fritbot quote bob`. Listeners look for anything said in any room the bot is in, but cannot take arguments and usually should be used sparingly to avoid being spammy.

To register a very simple command like the one in the next example, all you really need is the following:

	intent.service.registerCommand("say hi", self.sayHello, self, "Say Hello", "Says Hi")

The arguments to this are, in order:

* Regex, or list of regexes, that can trigger this command. Any valid regex is possible here.
* Function to execute which takes the argument pattern explained below
* self - this must always be the module itself; it is used in help functionality.
* Name of the command, used as the title in help functionality.
* Description of the command, stating usage and expected functionality.

The most simple command is below:

	@response
	def sayHello(self, bot, room, user, args):
		return "Hello, " + user['nick']
	
`@response` is a python decorator indicating that this function is a bot response; this wraps it in some logic that will allow the bot to automatically respond with the functions' return value no matter where the input came from. Other decorators available, which should be placed before `@response`, are `@admin`, which verifies that the user is an administrator, `@room_only` which will restrict access to the function to rooms only, and `@user_only` which will restrict access to only private chats to the bot. These can be used in combination.

The function itself takes four arguments: `bot` which is the actual FritBot class instance, `room` which is the Room object that the command was triggered in or `null` if it was a private chat, `user` which is the User object who triggered the function, and `args` which is either the arguments parsed from the command, or the match object of the regex in a listener. To actually cause the bot to respond to commands or listeners, simply have it return a string or unicode value. What happens in between the two is completely up to you - anything possible in python can be done.