function readySteadyGo() {
	$.ajaxSetup({
		"cache": false,
		"dataType": "json"
	});
	$("#login-button").click(retrieveToken).button();
	$("#logout-button").click(loggedOut).button({icons: {secondary:'ui-icon-power'}});
	initialLoginCheck();
}
