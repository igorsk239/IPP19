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

  $arg_parse = new tArguments();
  // $arg_parse->p_parse_script = False;
  // $arg_parse->p_int_script = False;
  // $arg_parse->p_parse_only = False;
  // $arg_parse->p_int_only = False;
  // $arg_parse->p_help = False;
  // $arg_parse->p_dir = False;
  // $arg_parse->p_rec = False;

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

  if(!$arg_parse->p_parse_script){
    $parse_file = "parse.php";
  }
  if(!$arg_parse->p_int_script){
    $int_file = "interpret.py";
  }





 ?>
