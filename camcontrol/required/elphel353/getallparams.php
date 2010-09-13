<?php

/*
 * gets all parameters on an Elphel 353 camera
 * 
 * Copyright (c) 2010 Michael Aschauer
 *
 * --------------------------------------------------------------------
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * ---------------------------------------------------------------------
 */

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

