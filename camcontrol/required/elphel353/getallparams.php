<?php

header("Content-Type: text/xml");
header("Pragma: no-cache\n");
echo "<?xml version=\"1.0\"?>\n";
echo "<camera>\n";

$all=get_defined_constants();
$prefix = "ELPHEL_";

foreach ($all as $key => $value) {
	if(strpos($key,$prefix) === false) {}
	else {
		if (strpos($key,$prefix) == 0)
		{
			$name = str_replace($prefix, "", $key);
			printf("<%s>%s</%s>\n",
				$name,
				elphel_get_P_value($value),
				$name 
			);
		}
	}
}

echo "</camera>\n";	
?>

