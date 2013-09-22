// Let's kick off the application

require([
  'cookies',
  'Navigation',
  'underscore',
  'backbone.min',
  'jquery.loadTemplate.min',
  'bootstrap.min'
], function(Cookies, Navigation, _, Backbone, jqueryLoadTemplate, bootstrap){
	var router,
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
						console.log("Not valid action", action)
					}
				} else {
					console.log("Navigating to front page")
				}
			});

			Backbone.history.start();
		}
	});

	var navigation = new Navigation();

	navigation.onLoaded = function () {		
		$('#nav_target').append(this.root);
		router = new AppRouter();
	}
	
});
