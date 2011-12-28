function processLogin(key, name, user) {
	createCookie("bot_key", key, 30);
	createCookie("bot_name", name, 30);
	createCookie("bot_user", user, 30);

	$("#user-name").html(name);
	$("#user-status").show();
	$("#login-request").hide();
	$("#login-popin").hide();
}

function loggedIn(data, status, jq) {
	console.log("logged in", data);
		processLogin(data.key, data.nick, data.user);
}

function loggedOut(jq, status, thrown) {
	console.log("logged out");
	eraseCookie("bot_key");
	eraseCookie("bot_name");
	eraseCookie("bot_user");
	$("#user-status").hide("blind");
	$("#login-request").show();
}

function showUnauthorized(jq, status, thrown) {
	console.log("unauthorized -", thrown);
}

function retrieveToken() {
	$.ajax("http://localhost:4886/auth/request?application=web%20admin%20panel", {
		"success": function(data, status, jq) {
			console.log(data, data.token)
			$("#token-time").html(data.timeout);
			$("#login-popin").show("blind");
			$("#token-input").val("authorize " + data.token).focus().select();

			$.getJSON("http://localhost:4886/auth/response/" + data.token, loggedIn);},

		"error": loggedOut,
		}
);
}

function initialLoginCheck() {
	var key = readCookie("bot_key");
	var user = readCookie("bot_user");
	var name = readCookie("bot_name");
	if (key != undefined) {
		console.log("already logged in ", name, user, key)
		$("#user-status").show();
		processLogin(key, name, user);
	} else {
		$("#login-request").show();
	}
}