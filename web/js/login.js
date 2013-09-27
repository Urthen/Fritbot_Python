// Let's kick off the application

define(['cookies', 'underscore'], function(Cookies, _){

	function LoginHandler() {
		this.apikey = null;
		this.username = null;
		this.useradmin = false;
	}

	LoginHandler.prototype.authenticate = function(key, remember) {
		$.ajax('/key/' + key, {
			success: _.bind(function (data) {
				console.log(data);
				}, this),
			error: function () {
				console.log("Not a key")
			}
		})
	};

	return LoginHandler;
});
