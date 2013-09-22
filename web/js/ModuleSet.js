// Let's kick off the application

define(['underscore'], function(_){

	var instance = null;

	function ModuleSet() {
		this.modules = {};
		this.sections = {};
		this.root = $("<ul class='nav nav-list'></ul>");

		$.get('/moduleassist', _.bind(function(data) {
			var count = 0;
			_.each(data.modules, function (value, key) {
				require(['../../' + value + "/index"], _.bind(function (module) {
					module.uid = value;
					this.addModule(module);
					count += 1;
					if (count == Object.keys(data).length) {
						this.renderNav();
						if (this.onLoaded) {
							this.onLoaded();
						}
					}
				}, this));
			}, this);
		}, this));
	}

	ModuleSet.prototype.addModule = function (module) {
		this.modules[module.uid] = module

		if (this.sections[module.section]) {
			this.sections[module.section].push(module)
		} else {
			this.sections[module.section] = [module]
		}
	}

	ModuleSet.prototype.renderNav = function () {
		console.log("rendering nav...");
		_.each(this.sections, function (value, key) {
			this.root.append("<li class='nav-header'>" + key + "</li>")
			_.each(value, function(item, key) {
				this.root.append("<li id='link_" + item.uid + "'><a href='#" + item.uid + "'>" + item.name + "</a></li>")
			}, this)
		}, this)
	}

	return ModuleSet;
});
