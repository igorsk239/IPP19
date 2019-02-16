<?php

$keywords = array(
  "move", "createframe", "pushframe", "popframe", "defvar", "call", "return",
  "pushs", "pops",
  "add", "sub", "mul", "idiv", "lt", "gt", "eq", "and", "or", "not", "int2char", "stri2int",
  "read", "write",
  "concat", "strlen", "getchar", "setchar",
  "type",
  "label", "jump", "jumpifeq", "jumpifneq", "exit",
  "dprint", "break",
  "int", "string", "bool", "nil",
  "true", "false",
  "gf", "lf", "tf"
);
class tToken {
  public $type;
  public $data;
  public $last;
}
class tIdentifier {
  public $stringSearch;
  public $varSearch;
  public $numberSearch;
}
class aStatp {
  public $ispresent;
  public $stat_list;
  public $statistics;
}

abstract class tokenType {
  const start = 100;
  const header = 101;
  const EOL = 102;
  const loadNumber = 103;
  const charStream = 104;
  const identifyStream = 105;
  const marker = 106;
  const commentary = 107;

  const i_move = 110;
  const i_createframe = 111;
  const i_pushframe = 112;
  const i_popframe = 113;
  const i_defvar = 114;
  const i_call = 115;
  const i_return = 116;
  const i_pushs = 117;
  const i_pops = 118;
  const i_add = 119;
  const i_sub = 120;
  const i_mul = 121;
  const i_idiv = 122;
  const i_lt = 123;
  const i_gt = 124;
  const i_eq = 125;
  const i_and = 126;
  const i_or = 127;
  const i_not = 128;
  const i_int2char = 129;
  const i_stri2int = 130;
  const i_read = 131;
  const i_write = 132;
  const i_concat = 133;
  const i_strlen = 134;
  const i_getchar = 135;
  const i_setchar = 136;
  const i_type = 137;
  const i_label = 138;
  const i_jump = 139;
  const i_jumpifeq = 140;
  const i_jumpifneq = 141;
  const i_exit = 142;
  const i_dprint = 143;
  const i_break= 144;

  const d_int = 145;
  const d_string = 146;
  const d_bool = 147;
  const d_nil = 148;

  const b_true = 149;
  const b_false = 150;

  const f_gf = 151;
  const f_lf = 152;
  const f_tf = 153;

  const identifier = 200;
  const number = 201;
  const stringStream = 202;
}

function arg_parse($argc, $argv){

  if($argc == 2 && ($argv[1] === "--help" || $argv[1] === "-help")){
      echo 'Usage: php7.3 parse.php | --help
            --help Prints help message'."\n";
  }
  // elseif($argc >= 2){
  //   fwrite(STDERR, "Usage of innapropriate argumets run parse.php --help for further details\n");
  //   exit(); //appropriate exit code
  // }
}

function read_stream(){
  global $array_stream;
  $array_key = 0;

  while($character = fgetc(STDIN)){
    $array_stream[$array_key] = $character;
    $array_key++;
  }
  global $key_val;
  global $c_commentary;
  $c_commentary = 0;
  $key_val = 0;
}
function preset_identifier()
{
  global $identifier;
  $identifier = new tIdentifier();
  $identifier->stringSearch = NULL;
  $identifier->varSearch = NULL;
  $identifier->numberSearch = NULL;

}
function init_token(){
  global $token;
  $token = new tToken();
  $token->data = NULL;
  $token->type = tokenType::start;
  $token->last = True;
}

function identify_operand(){
  global $token;
  global $identifier;
  switch ($token->data) {
    case 'string':
      $identifier->stringSearch = True;
      break;
    case 'int':
      $identifier->numberSearch = True;
      break;
    default:
      if(preg_match("/^(LT)|(GT)|(LF)$/", $token->data)){
        $identifier->varSearch = True;
      }
      break;
  }
}
function isset_identif(){
  global $token;
  global $identifier;
  if($identifier->stringSearch){
    $token->type = tokenType::d_string;
  }
  elseif($identifier->varSearch){
    $token->type = tokenType::identifier;
  }
  elseif($identifier->numberSearch){
    $token->type = tokenType::number;
  }
}

function get_token(){
  global $token;
  global $identifier;
  global $array_stream;
  global $key_val;
  global $keywords;

  global $c_commentary;

  $token_end = True;
  $token_type = tokenType::start;
  init_token();

  while($token_end){
    if($key_val === array_key_last($array_stream)){   //end of Array works only for PHP7.3!!!!
      $token->last = False;
    }

    switch ($token_type) {
      case tokenType::start:
      {
        if($array_stream[$key_val] === "."){
          $token_type = tokenType::header;
          break;
        }
        elseif($array_stream[$key_val] === "@"){
          $token->data = $array_stream[$key_val];
          $token->type = tokenType::marker;
          $key_val++;
          $token_end = False;
          break;
        }
        elseif($array_stream[$key_val] === "#"){
          $token_type = tokenType::commentary;
          break;
        }
        elseif($array_stream[$key_val] === PHP_EOL){
          $token_type = tokenType::EOL;
          break;
        }
        elseif($array_stream[$key_val] === "\t" || $array_stream[$key_val] === " "){ //  //elseif(preg_match("[ \t]", $array_stream[$key_val])){
          $key_val++;
        }
        elseif(ctype_alpha($array_stream[$key_val]) || ctype_digit($array_stream[$key_val]) || preg_match("/^_|\-|\$|&|%|\*|!|\?$/", $array_stream[$key_val])){
          $token_type = tokenType::charStream;
          break;
        }
        else {
          fwrite(STDERR, "ERROR : Input doesn't start with .IPPcode19 header\n");
          exit();#appropriate exit code
        }
        break;
      }
      case tokenType::header:
      {
        while(1){
          if($array_stream[$key_val] === PHP_EOL){
            if(preg_match("/^.ippcode19$/", strtolower($token->data))){
              $token->type = tokenType::header;
              $token_end = False;
              break;
            }
            else {
              fwrite(STDERR,"ERROR : Innapropriate header detected\n");
              exit();//no ippcode header;
            }
          }
          $token->data .= $array_stream[$key_val];
          $key_val++;
        }
        break;
      }
      case tokenType::EOL:
      {
        $token->data = $array_stream[$key_val];
        $token->type = tokenType::EOL;
        $key_val++;
        preset_identifier();
        $token_end = False;
        break;
      }
      case tokenType::commentary:
      {
        while($array_stream[$key_val] !== PHP_EOL)
        {
          $key_val++;
        }
        $c_commentary++;
        $token_type = tokenType::EOL;
        break;
      }
      case tokenType::charStream:
      {
        while(1){
          if($array_stream[$key_val] === " " || $array_stream[$key_val] === "\t" || $array_stream[$key_val] === "@"){
            $token_type = tokenType::identifyStream;
            break;
          }
          elseif($array_stream[$key_val] === PHP_EOL){
            $token_type = tokenType::identifyStream;
            break;
          }
          $token->data .= $array_stream[$key_val];
          $key_val++;
        }
        break;
      }
      case tokenType::identifyStream:
      {
        if(preg_match("/^[a-zA-Z_\-\$&%\*!?][a-zA-Z_\-\$&%\*!?0-9]*$/", $token->data)){ //matching the identifier
          $token->type = tokenType::identifier;
          foreach ($keywords as $key => $value) { //searching for keyword
            $match_pattern = "/\b" . "$value" . "\b/i";
            if(preg_match($match_pattern, strtolower($token->data))){
              $token->type = $key + 110;
              if(preg_match("/^(bool)|(int)|(string)|(nil)|(gf)|(lf)|(tf)$/", $token->data)){
                identify_operand();
              }
              break;
            }
          }
          $token_end = False;
          break;
        }
        if(preg_match("/^[+|-]?[1-9][0-9]*|[+|-][0]|[0]$/", $token->data)){  //matching numbers
          $token->type = tokenType::number;
          $token_end = False;
        }
        elseif(preg_match("/^([ěščřžýáíéóúůďťňĎŇŤŠČŘŽÝÁÍÉÚŮa-zA-Z0-9]|([\\\\][0-9]{3})?)*$/", $token->data)){
          $token->type = tokenType::stringStream;
          $token_end = False;
        }
        else {
          fwrite(STDERR,"ERROR : LEX : detected\n");
          echo "$token->data|\n";
          exit();
        }
        isset_identif();
        break;
      }

      default:
        break;
    }
  }
}


arg_parse($argc, $argv);
read_stream();
preset_identifier();
init_token();

/*  Header occurence check*/
get_token();
if($token->type === tokenType::header)
{
  get_token();
  if($token->type !== tokenType::EOL){
    fwrite(STDERR, "ERROR : HEADER : Header must be followed by new line\n");
    exit();
  }
}
else{
  fwrite(STDERR, "ERROR : HEADER : Missing header in format .ippcode19\n");
  exit();
}
$header_check = 1;


//DEBUG
// for($i = 0; $i < 23 ; $i++){
//   get_token();
//   echo "token data: " . $token->data . " type: " . $token->type . "\n";
//
// }
# XML GENERATION

function xml_token_type($t_type){
  switch ($t_type) {
    case tokenType::d_int:
      return "int";
    case tokenType::d_string:
      return "string";
    case tokenType::d_bool:
      return "bool";
    case tokenType::d_nil:
      return "nil";
    case tokenType::identifier:
      return "var";
    case tokenType:::
      return "label";
    case tokenType:::
      return "type";
    default:
      # code...
      break;
  }
}
function xml_add_symbol(){

}

function xml_add_label(){

}

function xml_add_var(){

}

function xml_special_char($t_data){

  if(preg_match("/\"/", $t_data)) str_replace("\"", "&quot", $t_data);
  elseif(preg_match("\'", $t_data)) str_replace("\'", "&quot", $t_data);
  elseif(preg_match("&", $t_data)) str_replace("&", "&amp", $t_data);
  elseif(preg_match("<", $t_data)) str_replace("<", "&lt", $t_data);
  elseif(preg_match(">", $t_data)) str_replace(">", "&gt", $t_data);
}



#   SYNTAX ANALYSIS
function eol_identify(){
  global $token;

  get_token();
  if($token->type !== tokenType::EOL){
    fwrite(STDERR, "ERROR : SYNTAX : End of line <eol> expected : last token: $token->data\n");
    exit();
  }
}
function var_identify(){
  global $token;
  $error_val = False;

  get_token();
  if($token->type >= tokenType::f_gf && $token->type <= tokenType::f_tf){
    $arg1->addAttribute('type',xml_token_type($token->type));
    $arg1[0] = $token->data;
    get_token();
    if($token->type === tokenType::marker){
      $arg1[0] .= $token->data;
      get_token();
      if($token->type !== tokenType::identifier){
        $error_val = True;
      }
      $arg1[0] .= $token->data;
    }
    else $error_val = True;
  }
  else $error_val = True;

  if($error_val){
    fwrite(STDERR, "ERROR : SYNTAX : Variable <var> expected : last token: $token->data\n");
    exit();
  }
}
function symb_identify(){
  global $token;
  $error_val = False;

  get_token();
  if($token->type === tokenType::d_int){
    get_token();
    if($token->type === tokenType::marker){
      get_token();
      if($token->type !== tokenType::number){
        $error_val = True;
      }
    }
    else $error_val = True;
  }
  elseif($token->type === tokenType::d_string){
    get_token();
    if($token->type === tokenType::marker){
      get_token();
      if($token->type !== tokenType::stringStream){
        $error_val = True;
      }
    }
    else $error_val = True;
  }
  elseif($token->type === tokenType::d_bool){
    get_token();
    if($token->type === tokenType::marker){
      get_token();
      if($token->type === tokenType::b_true || $token->type === tokenType::b_false){
        ;
      }
      else $error_val = True;
    }
    else $error_val = True;
  }
  elseif($token->type === tokenType::d_nil){
    get_token();
    if($token->type === tokenType::marker){
      get_token();
      if($token->type !== tokenType::d_nil){
        $error_val = True;
      }
    }
    else $error_val = True;
  }
  elseif($token->type >= tokenType::f_gf && $token->type <= tokenType::f_tf){
    get_token();
    if($token->type === tokenType::marker){
      get_token();
      if($token->type !== tokenType::identifier){
        $error_val = True;
      }
    }
    else $error_val = True;
  }
  else $error_val = True;

  if($error_val){
    fwrite(STDERR, "ERROR : SYNTAX : Symbol <symb> expected : last token: $token->data\n");
    exit();
  }
}

$v_statp = new aStatp();
$v_statp->ispresent = 0;
$v_statp->stat_list = [];
$statp_stats[1] = 0;
$statp_stats[2] = 0;
$statp_stats[3] = 0;

$program = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?>'.'<program></program>');
$program->addAttribute('language', 'IPPcode19');
$instr_ord = 0;

while($token->last){
  $statp_stats[1]++;
  get_token();
  if($token->type !== tokenType::EOL){
    $instr_ord++;
    $instruction = $program->addChild('instruction');
    $instruction->addAttribute('order', $instr_ord);
    $instruction->addAttribute('opcode', strtoupper($keywords[($token->type)-110]));
  }



  switch ($token->type) {
    case tokenType::header:
          eol_identify();
          $header_check++;
          $statp_stats[1]--;
          break;
    case tokenType::i_createframe:
    case tokenType::i_pushframe:
    case tokenType::i_return:
    case tokenType::i_break:
          eol_identify();
          break;

    case tokenType::i_label:
          $statp_stats[2]++;
    case tokenType::i_call:
    case tokenType::i_jump:
          get_token();
          if($token->type !== tokenType::identifier){
            fwrite(STDERR, "ERROR : SYNTAX : Label <label> expected : last token: $token->data\n");
            exit();
          }
          if($token->type === tokenType::i_jump || $token->type === tokenType::i_call) $statp_stats[3]++;
          eol_identify();
          break;
    case tokenType::i_defvar:
    case tokenType::i_pops:
          $arg1 = $instruction->addChild('arg1');
          var_identify();
          eol_identify();
          break;
    case tokenType::i_pushs:
    case tokenType::i_write:
    case tokenType::i_exit:
    case tokenType::i_dprint:
          symb_identify();
          eol_identify();
          break;
    case tokenType::i_move:
    case tokenType::i_int2char:
    case tokenType::i_strlen:
    case tokenType::i_type:
    case tokenType::i_not:
          var_identify();
          symb_identify();
          eol_identify();
          break;
    case tokenType::i_add:
    case tokenType::i_sub:
    case tokenType::i_mul:
    case tokenType::i_idiv:
    case tokenType::i_lt:
    case tokenType::i_gt:
    case tokenType::i_eq:
    case tokenType::i_and:
    case tokenType::i_or:
    case tokenType::i_stri2int:
    case tokenType::i_concat:
    case tokenType::i_getchar:
    case tokenType::i_setchar:
          var_identify();
          symb_identify();
          symb_identify();
          eol_identify();
          break;
    case tokenType::i_jumpifeq:
    case tokenType::i_jumpifneq:
          get_token();
          if($token->type !== tokenType::identifier){
            fwrite(STDERR, "ERROR : SYNTAX : Expected <label> : last token: $token->data\n");
            exit();
          }
          symb_identify();
          symb_identify();
          eol_identify();
          $statp_stats[3]++;
          break;
    case tokenType::i_read:
          var_identify();
          get_token();
          if($token->type < d_string || $token->type > d_bool){
            fwrite(STDERR, "ERROR : SYNTAX : Expected <type> : last token: $token->data\n");
            exit();
          }
          break;
    case tokenType::EOL:
          $statp_stats[1]--;
          break;
    default:
      # code...
      break;
  }
}

if($header_check != 1){
  fwrite(STDERR, "ERROR : HEADER : Multiple headers detected\n");
  exit();
}

foreach ($argv as $key => $value) {
  if(preg_match("/(\-\-stats=)|(\-\-loc)|(\-\-comments)|(\-\-labels)|(\-\-jumps)/",$argv[$key])){
    array_push($v_statp->stat_list, $argv[$key]);
    if(preg_match("/(\-\-stats=)/", $argv[$key])){
      array_pop($v_statp->stat_list);
      $file_stat = substr($argv[$key], 8); //file name
      if(!file_exists($file_stat)){
        fwrite(STDERR, "ERROR : FILE\n");
        exit();
      }
      $v_statp->ispresent++;
    }
  }
  elseif(preg_match("/(parse.php)/", $argv[$key])){
      array_pop($v_statp->stat_list);
  }
  else {
    fwrite(STDERR, "ERROR : ARGUMENTS : unknown argument $value use --help\n");
    exit();
  }
}

foreach ($v_statp->stat_list as $key => $value) {
  switch ($value) {
    case '--loc':
      file_put_contents($file_stat, "$statp_stats[1]\n", FILE_APPEND);
      break;
    case '--comments':
      file_put_contents($file_stat, "$c_commentary\n", FILE_APPEND);
      break;
    case '--labels':
      file_put_contents($file_stat, "$statp_stats[2]\n", FILE_APPEND);
      break;
    case '--jumps':
      file_put_contents($file_stat, "$statp_stats[3]\n", FILE_APPEND);
      break;
    default:
      break;
  }
}
if($v_statp->ispresent !== 1 && !empty($v_statp->stat_list)){
  fwrite(STDERR, "ERROR : STATP : --stats not present\n");
  exit(10);
}

/*
$program = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?>'.'<program></program>');
$program->addAttribute('language', 'IPPcode19');
*/
$array_stream = array_values($array_stream);
echo "keyval : $key_val  arrkey : $array_key   \n";
$key_val = 0;
echo "keyval : $key_val  arrkey : $array_key   \n";
while($token->last){
  get_token();
  echo "$token->data\n";
}

 ?>
