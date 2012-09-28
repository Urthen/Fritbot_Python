FritBot - The Angriest Bot
==========================

Introduction
------------

FritBot is a bot designed, in theory, to be a largely service-independent, modularly expandable chat bot. In reality, he mostly just yells indecent things at you and breaks himself. Use with caution.

Installation & Setup
--------------------

Prerequisites: Before starting, you should have installed virtualenv and virtualenvwrapper with `pip install virtualenv virtualenvwrapper` if you don't have them already. Additionally,
you should install mongodb as platform appropriate.

1. Fork this repo so you can make your own changes / additions.
2. Checkout _your_ repo to your local machine.
3. Make a virtual environment for fritbot with `mkvirtualenv fb`. You can leave this virtual environment with `deactivate` and get back in later with `workon fb`. Read the virtualenvwrapper documentation for more info.
4. Install requirements with `pip install -r requirements.txt`
5. Run mongodb with `./go-mongo.sh` if you don't already have some way to start mongo. This script will create a logs directory and output all logs there.
6. You will need to copy the sample config and name it `config.py`. You will need to edit, at minimum, the Jabber settings (assuming you are using Jabber). You will likely also want to edit the enabled modules.
7. Run the bot with `twistd -ny jabberbot.tac` to start in daemonzied mode: All output will be logged to the console, useful for debugging. Press ctrl-c to exit.
8. If you would like to run a more permanent instance, run the bot with `-y` instead of `-ny`. Output will be logged to file and the bot must be shut down via a shutdown command from chat or kill command from the console.

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