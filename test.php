<?php
/*
TODO
parse.php
-dokumentacia kodu
-nazov premennej LF@move  - HACK
-obsah string@09256 - HACK
-komentar hned za operandom - HACK
-exit codes	-	HACK
-statp opravit pracu so suborom a error codes - HACK
-komentar na riadku hned za .ippcode19  - HACK
-male pismena - Lf lF v oznaceni ramca - HACK
-FAlse FALSE false - HACK
- .ippcode19 createframe  - HACK
-instrukcia na rovnakom riadku ako .ippcode19
- LF@5a_55-$&amp;%*!?string - HACK

test.php
-dokumentacia kodu
-otestovat parametre vstupne  - HACK
-usage v test.php a parse.php - HACK
-recursive zanorovanie do directories + oddelit spustanie testov do funkcie - HACK
- *.rc subory ak nie su vytvorene - chyba navratova hodnota zjavne  - HACK
- generate HTML on empty dir with tests - HACK
- add test names to output  - HACK
- navratove hodnoty testov ktoru brat kedy
- separatne premenne pre dir testy a celkove uspesnosti

*/


  class tArguments {
    public $p_help;
    public $p_dir;
    public $p_rec;
    public $p_parse_script;
    public $p_int_script;
    public $p_parse_only;
    public $p_int_only;
  }

  function prepend($text1, $text2) {
     return $text2 . $text1;
  }

  function succ_test_html($test_counter, $test_name){
    echo "<font size=\"2\" color=\"black\">$test_counter. $test_name TEST :  passed </font><br>\n";
  }
  function unsucc_test_html($test_counter, $test_name){
    echo "<font size=\"2\" color=\"red\">$test_counter. $test_name TEST :  failed </font><br>\n";
  }

  function parse_directory($files){

    foreach ($files as $key => $t_name) {
      if(strpos($t_name, ".src")) $srcfiles[$key++] = $t_name;
    }
    return $srcfiles;
  }

  function run_tests($srcfiles, $arg_parse, $int_file, $parse_file, $dir_file, $rec){
    global $succ_test;
    global $unsucess_test;
    global $test_number;

    foreach ($srcfiles as $key => $value) {
      $test_number++;
      if(!$rec) $value = prepend($value, $dir_file);

      if(!file_exists(str_replace(".src", ".rc", $value))){
        $f_rc = fopen(str_replace(".src", ".rc", $value), "w+");
        fwrite($f_rc, "0");
        $rc_val = "0";
      }
      else {
        $f_rc = fopen(str_replace(".src", ".rc", $value), "r");
        $rc_val = fgets($f_rc);
      }

      if(!file_exists(str_replace(".src", ".in", $value))){
        $f_in = fopen(str_replace(".src", ".in", $value), "w");
      }
      else {
        $f_in = fopen(str_replace(".src", ".in", $value), "r");
      }

      if(!file_exists(str_replace(".src", ".out", $value))){
        $f_out = fopen(str_replace(".src", ".out", $value), "w");
      }
      else {
        $f_out = fopen(str_replace(".src", ".out", $value), "r");
      }

      if($arg_parse->p_parse_only || (!$arg_parse->p_parse_only && !$arg_parse->p_int_only)){
        exec("timeout 1 php7.3 $parse_file < $value  2> /dev/null > parse_temp.out ");
        $ret_val = exec("echo $?");
        if($ret_val === 124){
          $unsucess_test++;
          unsucc_test_html($test_number, $value);
        }
        elseif($ret_val !== $rc_val && ($rc_val > 0 && $rc_val <= 23)){
          // echo "$rc_val---\n";
          $unsucess_test++;
          unsucc_test_html($test_number, $value);
        }
        else{
          exec("java -jar /pub/courses/ipp/jexamxml/jexamxml.jar $f_out parse_temp.out diffs.xml  /D /pub/courses/ipp/jexamxml/options");
          $ret_val = exec("echo $?");
          if($ret_val !== "0"){
            $unsucess_test++;
            unsucc_test_html($test_number, $value);
          }
          else {
            //if($arg_parse->p_parse_only){
              $succ_test++;
              succ_test_html($test_number, $value);
            //}
          }
        }
      }
      elseif($arg_parse->p_int_only || (!$arg_parse->p_parse_only && !$arg_parse->p_int_only)){
        exec("python3.6 $int_file --source=parse_temp.out --input=$f_in > int_temp.out");
        $ret_val = exec("echo $?");
        if($ret_val !== $rc_val){
          $unsucess_test++;
          unsucc_test_html($test_number, $value);
        }
        else{
          $diff_out = "";
          exec("diff $int_out $f_out > $diff_out");
          exec("echo $?");
          if($ret_val !== "0"){
            $unsucess_test++;
            unsucc_test_html($test_number, $value);
          }
          else {
            $succ_test++;
            succ_test_html($test_number, $value);
          }
        }
      }
      fclose($f_rc);
      fclose($f_in);
      fclose($f_out);
    }
  }

  $arg_parse = new tArguments();

  $succ_test = 0;
  $unsucess_test = 0;
  $test_number = 0;

  foreach ($argv as $key => $value) {
    if(substr($value, 0, 15) === "--parse-script="){
      $arg_parse->p_parse_script = True;
      $parse_file = substr($argv[$key], 15);
    }
    elseif(substr($value, 0, 13) === "--int-script="){
      $arg_parse->p_int_script = True;
      $int_file = substr($argv[$key], 13);
    }
    elseif(substr($value, 0, 12) === "--directory="){
      $arg_parse->p_dir = True;
      $dir_file = substr($argv[$key], 12);
      if(substr($dir_file, -1) !== "/") $dir_file .= "/";
    }
    elseif(preg_match("/^(\-\-help)+$/", $value)){
      $arg_parse->p_help = True;
    }
    elseif(preg_match("/^(\-\-recursive)+$/", $value)){
      $arg_parse->p_rec = True;
    }
    elseif(preg_match("/^(\-\-parse-only)+$/", $value)){
      $arg_parse->p_parse_only = True;
    }
    elseif(preg_match("/^(\-\-int-only)+$/", $value)){
      $arg_parse->p_int_only = True;
    }
    elseif(substr( $value, 0, 15) === "test.php"){
      ;
    }
    else{
      fwrite(STDERR,"ERROR : ARGUMENTS : Unknown argument: $value detected\n");
      exit();
    }

  }

  if($arg_parse->p_help && $argc > 2){
    fwrite(STDERR, "ERROR : ARGUMENTS : Argument after --help detected\n");
    exit(10);
  }
  elseif($arg_parse->p_int_only && $arg_parse->p_parse_only){
    fwrite(STDERR, "ERROR : ARGUMENTS : Combination of unrelated arguments detected\n");
    exit(10);
  }
  elseif($arg_parse->p_help) {
    fwrite(STDIN,
    "Usage: php7.3 test.php | --help | [--directory=path] [--recursive] [--parse-script=file] [--int-script=file] | [--parse-only] | [--int-only]
            Script for automatic testing\n
              --help                help message
              --directory=path      path to directories with tests
              --recursive           recursive search in directories
              --parse-script=file   parse.php file which is going to be used
              --int-script=file     interpret.py file which is going to be used
              --parse-only          running tests only for parse.php
              --int-only            running tests only for interpret.py

    Script will serve for purpose of automatic testing of application parse.php and interpret.py.
    Script will search given directory with tests and use them for automatic testing of proper functionality
    both previously mentioned applications. Therefor it will generate HTML5 file with information about test
    succession to STDIN.\n");
    exit(0);
  }

  /*  Creating HTML page with results  */
  echo "<!DOCTYPE HTML>\n";
  echo "<html>\n";
  echo "<head>\n";
  echo "<meta charset=\"utf-8\">\n";
  echo "<title>IPP project</title>\n";
  echo "</head>\n";
  echo "<body>\n";
  echo "<h1>IPP project<h1>\n";
  echo "<h1>author: Igor Ignac<h1>\n";


  if(!$arg_parse->p_parse_script){
    $parse_file = "parse.php";
  }
  if(!$arg_parse->p_int_script){
    $int_file = "interpret.py";
  }
  if(!$arg_parse->p_dir){
    $dir_file = getcwd();
    $dir_file .= "/";
  }


  $files = scandir($dir_file);
  unset($key);
  $subdirs = [];
  $srcfiles = [];

  /*  Parsing given directory -- not recursive  */
  if(!$arg_parse->p_rec){

    echo "<font size=\"6\" color=\"black\">Testing directory : $dir_file</font><br>\n";
    $srcfiles = parse_directory($files);

    unset($key);
    if(isset($srcfiles)){
      run_tests($srcfiles, $arg_parse, $int_file, $parse_file, $dir_file, 1);
    }
    else {
      echo "<font size=\"2\" color=\"red\">Given directory doesn't contain any test</font><br>\n";
    }
    echo "<font size=\"5\" color=\"black\">Directory results :</font><br>\n";
    echo "<font size=\"2\" color=\"black\">Tests total: $test_number</font><br>\n";
    echo "<font size=\"2\" color=\"green\">Tests passed: $succ_test</font><br>\n";
    echo "<font size=\"2\" color=\"red\">Tests failed: $unsucess_test</font><br>\n";
  }
  else {
    /***************************************************************************************
    *    Title: Recursive File Search (PHP)
    *    Author: Jan Hančič
    *    Date: Dec 7 2009 at 14:46
    *    Availability: https://stackoverflow.com/questions/1860393/recursive-file-search-php
    *
    ***************************************************************************************/
    $it = new RecursiveDirectoryIterator($dir_file);
    $display = Array ( 'src' );
    foreach(new RecursiveIteratorIterator($it) as $file)
    {
        if (in_array(strtolower(array_pop(explode('.', $file))), $display))
            $srcfiles[] = $file;
    }
    /***************************************************************************************
    *   end of citation
    ****************************************************************************************/
    if(isset($srcfiles)){
      run_tests($srcfiles, $arg_parse, $int_file, $parse_file, $dir_file, 1);
    }

  }

  echo "<font size=\"5\" color=\"black\">Results for all tests :</font><br>\n";
  echo "<font size=\"2\" color=\"black\">Tests total: $test_number</font><br>\n";
  echo "<font size=\"2\" color=\"green\">Tests passed: $succ_test</font><br>\n";
  echo "<font size=\"2\" color=\"red\">Tests failed: $unsucess_test</font><br>\n";
  echo "</body>\n";
  echo "</html>\n";

  exec("rm -rf parse_temp.out 2>& 1");
  if(!$arg_parse->p_parse_only){
    exec("rm -rf int_temp.out 2>& 1");
  }
 ?>
