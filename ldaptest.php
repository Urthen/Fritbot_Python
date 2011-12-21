<html>
<head>
<title>Test</title>
</head>
<body>
<?php

function getLDAPEmail($uid) {
	$server='lab-ldap01.lab';
	$admin='ou=People,dc=bazaarvoice,dc=com';
	
	$dn="uid=".",".$admin;
	
	$ds=ldap_connect($server); 
	
	if ($ds) {
	    $r=ldap_bind($ds, $dn);
	    if(!$r) return "ERROR";
	    
	    $filter="(uid=$uid)";
		$justthese = array("ou", "sn", "givenname", "mail");
		
		$sr=ldap_search($ds, $admin, $filter, $justthese);
		
		$info = ldap_get_entries($ds, $sr);
		
	    ldap_close($ds);
		return $info[0]['mail'][0];
		
	} else {
	    return "ERROR";
	}

}


echo "Your email is: " . getLDAPEmail($_SERVER['PHP_AUTH_USER']);

#echo "<br><br>(" . $_SERVER['PHP_AUTH_PW'] . ")";

?>
</body>
</html>
