<?php

function convert($s) {
    // clean up
    $s = trim($s, "\" ");
   
    // check if value is in HEX
    if(strtoupper(substr($s, 0, 2))=="0X")
        return intval(hexdec($s));
    else
        return intval($s);
}

$param = array();
foreach($_GET as $key => $val) {
    $param[$key] = convert($val);
}

// parameters are set X frames in the future
if (isset($_GET['framedelay']))
	$frame_delay = $_GET['framedelay'];
else
	$frame_delay = 3; // default in 3 frames

// set parameters
$set_frame = elphel_set_P_arr ($param, elphel_get_frame() + $frame_delay);

for($i=0;$i<$frame_delay;$i++)
	elphel_wait_frame();

include("getparams.php");


?>
