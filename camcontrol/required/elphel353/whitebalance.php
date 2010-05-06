<?php
/*!*******************************************************************************
*! FILE NAME  : whitebalance.php
*! DESCRIPTION: Demo script to balance white
*! Copyright (C) 2008 Elphel, Inc
*! -----------------------------------------------------------------------------**
*!
*!  This program is free software: you can redistribute it and/or modify
*!  it under the terms of the GNU General Public License as published by
*!  the Free Software Foundation, either version 3 of the License, or
*!  (at your option) any later version.
*!
*!  This program is distributed in the hope that it will be useful,
*!  but WITHOUT ANY WARRANTY; without even the implied warranty of
*!  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*!  GNU General Public License for more details.
*!
*!  You should have received a copy of the GNU General Public License
*!  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*! -----------------------------------------------------------------------------**
*!  $Log: whitebalance.php,v $
*!  Revision 1.3  2008/03/20 22:33:43  elphel
*!  cleanup, returns xml now
*!
*!  Revision 1.2  2008/01/10 02:45:27  elphel
*!  Added debug/status information
*!
*!  Revision 1.1  2008/01/09 10:21:13  elphel
*!  added whitebalance.php - demo script to automatically adjust white balance
*!
*!
*/
//! elphel_white_balance ([double thrsh [, double minfrac [, double rscale [,double bscale]]]]);
//! Includes debug information that may be removed (everything with $balance_pars)

 $balance_pars=array(
  "RSCALE" =>       256,            //! red/green*256 (no auto - it is inside ccam.cgi)
  "BSCALE" =>       256,            //! blue/green*256 (no auto - it is inside ccam.cgi)
  "GSCALE" =>       256,            //! green1/green*256 (no auto - it is inside ccam.cgi)
  "GAINR" =>        512,            //! Red analog gain 2.0*256
  "GAING" =>        512,            //! Green1 (red row) analog gain 2.0*256
  "GAINB" =>        512,            //! Red analog gain 2.0*256
  "GAINGB" =>       512,            //! Green2 (blue row) analog gain 2.0*256
  );
  $xml = new SimpleXMLElement("<?xml version='1.0'?><white_balance/>");
  $xml->addChild ('pars');
  $xml->addChild ('before');


  $thrsh=0.98;
  $minfrac=0.01;
  $rscale=1.0;
  $bscale=1.0;
  $v=$_GET['thrsh'];   if (is_numeric ($v) && ($v > 0) && ($v <= 1)) $thrsh=$v;
  $v=$_GET['minfrac']; if (is_numeric ($v) && ($v > 0) && ($v <  1)) $minfrac=$v;
  $v=$_GET['rscale'];  if (is_numeric ($v) && ($v >= 0.1) && ($v <=  10.0)) $rscale=$v;
  $v=$_GET['bscale'];  if (is_numeric ($v) && ($v >= 0.1) && ($v <=  10.0)) $bscale=$v;
  $balance_pars=elphel_get_P_arr($balance_pars);
  foreach ($balance_pars as $key=>$value) {
    $xml->before->addChild ($key,$value);
  }
  $xml->pars->addChild ('thrsh',$thrsh);
  $xml->pars->addChild ('minfrac',$minfrac);
  $xml->pars->addChild ('rscale',$rscale);
  $xml->pars->addChild ('bscale',$bscale);
  $rslt= elphel_white_balance ($thrsh, $minfrac, $rscale, $bscale);
  $xml->addChild ('result',($rslt>=0)?"OK":"failure");
  if ($rslt>=0) {
     $xml->addChild ('after');
     elphel_program_sensor (1); //! (1) -  non-stop!
     $balance_pars=elphel_get_P_arr($balance_pars);
     foreach ($balance_pars as $key=>$value) {
       $xml->after->addChild ($key,$value);
     }
  }
  $sxml=$xml->asXML();
  header("Content-Type: text/xml");
  header("Content-Length: ".strlen($sxml)."\n");
  header("Pragma: no-cache\n");
  printf($sxml);
?>
