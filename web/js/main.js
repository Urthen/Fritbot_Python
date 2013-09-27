// Let's kick off the application

require([
  'navigation',
  'login',
  'backbone.min',
  'jquery.loadTemplate.min',
  'bootstrap.min'
], function(Navigation, Login, Backbone, jqueryLoadTemplate, bootstrap){
	var router, AppRouter, navigation, login;

	AppRouter = Backbone.Router.extend({
		routes: {
			// Default - catch all
			'*action': 'defaultAction'
		},
		initialize: function(){
			this.on('route:defaultAction', function (action) {
				if (action) {
					if (navigation.modules[action]) {
						console.log("Navigating to", navigation.modules[action].name);
						navigation.modules[action].render();
					} else {
						console.log("Not valid action", action);
					}
				} else {
					console.log("Navigating to front page");
				}
			});

			Backbone.history.start();
		}
	});

	navigation = new Navigation();
	login = new Login;

	navigation.onLoaded = function () {		
		$('#nav_target').append(this.root);
		router = new AppRouter();
	}

	$('#login-form').submit(function (event) {
		login.authenticate($("#login-key").val(), $("#login-remember").val());
		event.preventDefault();
	})
	
});
