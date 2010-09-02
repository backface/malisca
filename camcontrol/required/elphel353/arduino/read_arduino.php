#!/usr/local/sbin/php

<?php

$device = "/dev/ttyUSB0";

$ret = @exec("stty -F $device 9600 -parenb");
printf($ret);

$fp = @fopen($device, "r+");
if (!$fp)
	die("Could not open $device\n");

//stream_set_blocking($handle, 0);

$content= "";
$buffer = "";

while (1==1) {
	$buffer="";
	
    while ($buffer!=chr(10)) {
		$buffer = fread($fp, 1);
		$content .= $buffer;
	}

	//printf("IN: %s\n", $content);
	sscanf($content,"read:%d;%d;%d\n",
		$val_exposure,
		$val_trigger,
		$val_virtual);

	// EXPOSURE
	$params = array();
	
	$exposure = floatval($val_exposure / 100.);
	printf("exposure=%0.2f ms, ", $exposure);	
	$params["EXPOS"] = intval($exposure * 1000);
	$set_frame =  elphel_set_P_arr ($params, elphel_get_frame());


	// TRIGGER
	
	$params = array();

	if ($val_trigger < 1) $val_trigger=1;
	
	$trigger = 4;
	$trigger_period = 96000000 / (floatval($val_trigger) * 2);
	printf("trigger[ON]= %ld, ", $trigger_period);		

	$params["TRIG_PERIOD"] = intval($trigger_period);
	$set_frame =  elphel_set_P_arr ($params, elphel_get_frame());

	$params = array();		
	$params["TRIG"] = intval($trigger);
	$params["FP1000SLIM"] = $val_trigger;
	$set_frame =  elphel_set_P_arr ($params, elphel_get_frame() + 1);
				

	// VIRTUAL HEIGHT
	
	$params = array();
	
	if($val_virtual > 11)  {
		printf("virtual[ON]=%d", $val_virtual);
		$params["VIRT_HEIGHT"] = intval($val_virtual);
		$params["VIRT_KEEP"] = 1;
		
		$set_frame =  elphel_set_P_arr ($params, elphel_get_frame());
	} else {
		printf("virtual[OFF]");
		$params["VIRT_KEEP"] = 0;		
		$set_frame =  elphel_set_P_arr ($params, elphel_get_frame());	
	}

	printf(" ... updated frame #".$set_frame."\n");
	
	$content = "";
}
fclose ($handle);
?>
