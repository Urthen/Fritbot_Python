<?php

function getLDAPEmail($uid) {
	$server='lab-ldap02.lab';
	$admin='ou=People,dc=bazaarvoice,dc=com';
	
	$dn="uid=".$uid.",".$admin;
	$ds=ldap_connect($server); 
	
	if ($ds) {
	    $r=ldap_bind($ds);
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

echo "var USERID = '" . $_SERVER['PHP_AUTH_USER'] . "';\n";
echo "var EMAIL = '" . getLDAPEmail($_SERVER['PHP_AUTH_USER']) . "';";

?>
