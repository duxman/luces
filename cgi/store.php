<?
   $filename = $_POST["filename"];
   $contenido = json_encode($_POST["contenido"]);

   $postvalues = print_r ("$_POST", true);
   print "postvalues = ($postvalues) \r\n";
   print "filename = ($filename) \r\n";
   print "contenido = ($contenido) \r\n";

   $obj = json_decode($contenido);
   $json_data = json_encode($obj.JSON_PRETTY_PRINT);

   file_put_contents($filename, $json_data);
?>