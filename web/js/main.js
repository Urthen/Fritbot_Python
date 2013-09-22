// Let's kick off the application

require([
  'cookies',
  'ModuleSet',
  'underscore',
  'backbone.min',
  'jquery.loadTemplate.min',
  'bootstrap.min'
], function(Cookies, ModuleSet, _, Backbone, jqueryLoadTemplate, bootstrap){
	var router,
		AppRouter = Backbone.Router.extend({
		routes: {
			// Default - catch all
			'*action': 'defaultAction'
		},
		initialize: function(){
			this.on('route:defaultAction', function (action) {
				if (action) {
					if (moduleSet.modules[action]) {
						console.log("Navigating to", moduleSet.modules[action].name);
						moduleSet.modules[action].render();
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

	var moduleSet = new ModuleSet();

	moduleSet.onLoaded = function () {		
		$('#nav_target').append(this.root);
		router = new AppRouter();
	}
	
});
