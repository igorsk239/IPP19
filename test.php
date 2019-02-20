<?php

// import com.a7soft.examxml.ExamXML;
// import com.a7soft.examxml.Options;

  class tArguments {
    public $p_help;
    public $p_dir;
    public $p_rec;
    public $p_parse_script;
    public $p_int_script;
    public $p_parse_only;
    public $p_int_only;
  }


  function succ_test_html($test_counter){
    echo "<font size=\"2\" color=\"black\">$test_counter. TEST :  passed </font><br>\n";
  }
  function unsucc_test_html($test_counter){
    echo "<font size=\"2\" color=\"red\">$test_counter. TEST :  failed </font><br>\n";
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
    }
    elseif(substr($value, 0, 6) === "--help"){
      $arg_parse->p_help = True;
    }
    elseif(substr($value, 0, 11) === "--recursive"){
      $arg_parse->p_rec = True;
    }
    elseif(substr( $value, 0, 12) === "--parse-only"){
      $arg_parse->p_parse_only = True;
    }
    elseif(substr( $value, 0, 10) === "--int-only"){
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
    "Script will serve for purpose of automatic testing of application parse.php and interpret.py.
    Script will search given directory with tests and use them for automatic testing of proper functionality
    both previously mentioned applications. Therefor it will generate HTML5 file with information about test succession to STDIN\n");
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


  if(!$arg_parse->p_parse_script){
    $parse_file = "parse.php";
  }
  if(!$arg_parse->p_int_script){
    $int_file = "interpret.py";
  }
  if(!$arg_parse->p_dir){
    $dir_file = getcwd();
  }


  $files = scandir($dir_file);
  unset($key);
  $subdirs = "";

  /*  Parsing given directory -- not recursive  */
  if(!$arg_parse->p_rec){
    foreach ($files as $key => $t_name) {
      if(strpos($t_name, ".src")) $srcfiles[$key++] = $t_name;
      if(is_dir($t_name)){
        $subdirs[$key] = $files[$key];
        unset($files[$key]);
      }
    }
    unset($key);

    foreach ($srcfiles as $key => $value) {
      $test_number++;

      if(!file_exists(str_replace(".src", ".rc", $value))){
        $f_rc = fopen(str_replace(".src", ".rc", $value), "w");
        $txt = "0";
        fwrite($f_rc, $txt);
        $rc_val = fgets($f_rc,1024);
      }
      else {
        $f_rc = fopen(str_replace(".src", ".rc", $value), "r");
        $rc_val = fgets($f_rc,1024);
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
        exec("timeout 1 php7.3 $parse_file < $value > parse_temp.out");
        $ret_val = exec("echo $?");
        if($ret_val === 124){
          $unsucess_test++;
          unsucc_test_html($test_number);
        }
        elseif($ret_val !== $rc_val){
          $unsucess_test++;
          unsucc_test_html($test_number);
        }
        else{
          exec("java -jar /pub/courses/ipp/jexamxml/jexamxml.jar $f_out parse_temp.out diffs.xml  /D /pub/courses/ipp/jexamxml/options");
          $ret_val = exec("echo $?");
          if($ret_val !== "0"){
            $unsucess_test++;
            unsucc_test_html($test_number);
          }
          else {
            if($arg_parse->p_parse_only){
              $succ_test++;
              succ_test_html($test_number);
            }
          }
        }
        exec("rm parse_temp.out");
      }
      elseif($arg_parse->p_int_only || (!$arg_parse->p_parse_only && !$arg_parse->p_int_only)){
        exec("python3.6 $int_file --source=parse_temp.out --input=$f_in > int_temp.out");
        $ret_val = exec("echo $?");
        if($ret_val !== $rc_val){
          $unsucess_test++;
          unsucc_test_html($test_number);
        }
        else{
          $diff_out = "";
          exec("diff $int_out $f_out > $diff_out");
          exec("echo $?");
          if($ret_val !== "0"){
            $unsucess_test++;
            unsucc_test_html($test_number);
          }
          else {
            $succ_test++;
            succ_test_html($test_number);
          }
        }
        exec("rm int_temp.out");
      }
      fclose($f_rc);
      fclose($f_in);
      fclose($f_out);
      // fclose($parse_out);
      // fclose($int_out);

    }
  }

  echo "<font size=\"2\" color=\"black\">Tests total: $test_number</font><br>\n";
  echo "<font size=\"2\" color=\"black\">Tests passed: $succ_test</font><br>\n";
  echo "<font size=\"2\" color=\"black\">Tests failed: $unsucess_test</font><br>\n";
  echo "</body>\n";
  echo "</html>\n";

  exec("rm Resource.log");

  // print_r($files);
  // print_r($subdirs);
  // print_r($srcfiles);
 ?>
