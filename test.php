<?php
/**
 * @file: test.php
 * @author: Igor Ignác xignac00@fit.vutbr.cz
 * @name: Implementation of Project for IPP 2018/2019
 * @date 11.2.2019
 * Faculty: Faculty of Information Technology, Brno University of Technology
*/

  /**
  * Class for better argument parsing
  *
  * @access public
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

  /**
   * Prepends given $text2 before $text1
   * @param text1 string
   * @param text2 string prepended to text1
   * @return new string with prepended text1
   */
  function prepend($text1, $text2) {
     return $text2 . $text1;
  }

  /**
   * Generates HTML on a successfull test
   * @param test_counter order of the test
   * @param test_name name of the test
   */
  function succ_test_html($test_counter, $test_name){
    echo "<font size=\"2\" color=\"green\">$test_counter. $test_name TEST :  passed</font><br>\n";
  }

  /**
   * Generates HTML on a unsuccessfull test
   * @param test_counter order of the test
   * @param test_name name of the test
   * @param exp_val expected return value of the test
   * @param returned_val returned val by the test
   */
  function unsucc_test_html($test_counter, $test_name, $returned_val, $exp_val){
    echo "<font size=\"2\" color=\"red\">$test_counter. $test_name TEST :  failed</font><br>\n";
    if($returned_val === "124"){
      echo "<font size=\"2\" color=\"black\" style=\"margin-left: 15%\">Program got stucked killed the process</font><br>\n";
    }
    echo "<font size=\"2\" color=\"black\" style=\"margin-left: 15%\">Expected return value : $exp_val - returned : $returned_val</font><br>\n";
  }

  /**
   * Parses given directory and searches for .src files in it
   * @param files directory name
   * @return Array filled with files with .src extension
   */
  function parse_directory($files){

    foreach ($files as $key => $t_name) {
      if(strpos($t_name, ".src")) $srcfiles[$key++] = $t_name;
    }
    return $srcfiles;
  }

  /**
   * Runs all tests given in srcfiles

   * For every test also creates .in, .out and .rc file if it doesn't exist
   * already. Also writes 0 to .rc file. Funtion runs parse.php, interpret.py
   *
   * @param srcfiles source files with .src extenstion
   * @param arg_parse array filled with used command line arguments
   * @return Array filled with files with .src extension
   */
  function run_tests($srcfiles, $arg_parse, $int_file, $parse_file, $dir_file, $rec){
    global $succ_test;
    global $unsucess_test;
    global $test_number;

    $dir_succ = 0;
    $dir_failed = 0;
    $dir_total = 0;

    foreach ($srcfiles as $key => $value) {
      $test_number++;
      $current_dir = strrev(strstr(strrev($srcfiles[$key]), '/'));
      $next_dir = strrev(strstr(strrev($srcfiles[++$key]), '/')); //next dir -> used under
      $test_status = False;
      if($current_dir !== $next_dir){ // directory changed -> output sum Information about tests
        $dir_total = $dir_succ + $dir_failed;
        echo "<font size=\"5\" color=\"black\" style=\"margin-left: 10%\">Directory: $current_dir with results :</font><br>\n";
        echo "<font size=\"2\" color=\"green\" style=\"margin-left: 10%\">Tests passed: $dir_succ</font><br>\n";
        echo "<font size=\"2\" color=\"red\" style=\"margin-left: 10%\">Tests failed: $dir_failed</font><br>\n";
        echo "<font size=\"2\" color=\"black\" style=\"margin-left: 10%\">Tests total: $dir_total</font><br>\n";
        $dir_succ = $dir_failed = $dir_total = 0;

      }
      if(!$rec) $value = prepend($value, $dir_file);  //prepend path to test name

      /*  Extracting values from test files or creating new ones if not found */
      $e_src = $value;
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
        $e_in = str_replace(".src", ".in", $value);
      }
      else {
        $f_in = fopen(str_replace(".src", ".in", $value), "r");
        $e_in = str_replace(".src", ".in", $value);
      }

      if(!file_exists(str_replace(".src", ".out", $value))){
        $f_out = fopen(str_replace(".src", ".out", $value), "w");
        $e_out = str_replace(".src", ".out", $value);
      }
      else {
        $f_out = fopen(str_replace(".src", ".out", $value), "r");
        $e_out = str_replace(".src", ".out", $value);
      }

      /*  Run tests only for parser  or testing both  */
      if($arg_parse->p_parse_only || (!$arg_parse->p_parse_only && !$arg_parse->p_int_only)){
        if((intval($rc_val) >= 0 && intval($rc_val) <= 23)){
          exec("timeout 1 php7.3 $parse_file < $value 2> /dev/null > parse_temp.out ", $out, $ret_val);
          if($ret_val === 124){ //return value on timeout
            $unsucess_test++;
            $dir_failed++;
            unsucc_test_html($test_number, $value, $ret_val, $rc_val);
            $test_status = True;
          }
          elseif($ret_val !== intval($rc_val) && (intval($rc_val) >= 0 && intval($rc_val) <= 23)){  //catch return value from range 0 - 23
            $unsucess_test++;
            $dir_failed++;
            unsucc_test_html($test_number, $value, $ret_val, $rc_val);
            $test_status = True;
          }
          elseif(intval($rc_val) !== 0 && $ret_val === intval($rc_val))
          {
            $succ_test++;
            $dir_succ++;
            succ_test_html($test_number, $value);
            $test_status = True;
          }
          else{
            exec("java -jar /pub/courses/ipp/jexamxml/jexamxml.jar $e_out parse_temp.out", $out, $ret_val); //compare XML files with JExamXML  diffs.xml /D /pub/courses/ipp/jexamxml/options

            if($ret_val !== 0){
              $unsucess_test++;
              $dir_failed++;
              unsucc_test_html($test_number, $value , $ret_val, $rc_val);
              $test_status = True;
            }
            else {
              $succ_test++;
              $dir_succ++;
              succ_test_html($test_number, $value);
            }
          }
        }
      }
      /*  Running tests for interpreter */
      if($arg_parse->p_int_only || (!$arg_parse->p_parse_only && !$arg_parse->p_int_only)){
        if(!$arg_parse->p_parse_only && !$arg_parse->p_int_only) {
          $source_file = "parse_temp.out";
        }
        else {
          $source_file = $e_src;
        }
        if(!$test_status){
          exec("timeout 1 python3.6 $int_file --source=$source_file --input=$e_in 2> /dev/null > int_temp.out", $out, $ret_val);
          if(intval($ret_val) !== intval($rc_val)){
            $unsucess_test++;
            $dir_failed++;
            unsucc_test_html($test_number, $value, $ret_val, $rc_val);
          }
          elseif(intval($rc_val) !== 0 && $ret_val === intval($rc_val))
          {
            $succ_test++;
            $dir_succ++;
            succ_test_html($test_number, $value);
          }
          else{
            exec("diff int_temp.out $e_out 2> /dev/null", $out, $ret_val); //comparing output with diff
            if($ret_val !== 0){
              $unsucess_test++;
              $dir_failed++;
              unsucc_test_html($test_number, $value, $ret_val, $rc_val);
            }
            else {
              $succ_test++;
              $dir_succ++;
              succ_test_html($test_number, $value);
            }
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
  /*  Parsing arguments */
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
      exit(10);
    }

  }

  if($arg_parse->p_help && $argc > 2){  //arguments combined with --help
    fwrite(STDERR, "ERROR : ARGUMENTS : Argument after --help detected\n");
    exit(10);
  }
  elseif($arg_parse->p_int_only && $arg_parse->p_parse_only){
    fwrite(STDERR, "ERROR : ARGUMENTS : Forbidden combination of arguments detected\n");
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

  if(!file_exists($int_file)){
    fwrite(STDERR,"ERROR : FILE : Can not find file interpret.py\n");
    exit(11);
  }
  if(!file_exists($parse_file)){
    fwrite(STDERR,"ERROR : FILE : Can not find file parse.php\n");
    exit(11);
  }
  if(!is_dir($dir_file) || !file_exists($dir_file)){
    fwrite(STDERR,"ERROR : ARGUMENTS : Unknown argument: $value detected\n");
    exit(11);
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
      run_tests($srcfiles, $arg_parse, $int_file, $parse_file, $dir_file, 0);
    }
    else {
      echo "<font size=\"2\" color=\"red\">Given directory doesn't contain any test</font><br>\n";
    }
    echo "<font size=\"5\" color=\"black\" style=\"margin-left: 10%\">Directory results :</font><br>\n";
    echo "<font size=\"2\" color=\"black\" style=\"margin-left: 10%\">Tests total: $test_number</font><br>\n";
    echo "<font size=\"2\" color=\"green\" style=\"margin-left: 10%\">Tests passed: $succ_test</font><br>\n";
    echo "<font size=\"2\" color=\"red\" style=\"margin-left: 10%\">Tests failed: $unsucess_test</font><br>\n";
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

  /*  Clearing temporary files  */
  exec("rm -rf parse_temp.out Resource.log 2>& 1");
  if(!$arg_parse->p_parse_only){
    exec("rm -rf int_temp.out 2>& 1");
  }
  /* EOF */
 ?>
