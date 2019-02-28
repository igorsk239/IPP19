<?php
/**
 * @file parse.php
 * @author Igor Ignác xignac00@fit.vutbr.cz
 * @name Implementation of Project for IPP 2018/2019
 * @date 11.2.02019
 * Faculty: Faculty of Information Technology, Brno University of Technology
*/


/**
 * Array filled with keywords for language IPPcode19
 */
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

/**
* Class for token used in lexical and syntax analysis
*
* @access public
*/
class tToken {
  /**
   * Determines type of token which is used fo syntax analysis
   * @var type
 */
  public $type;

  /**
   * Contains data of particular token
   * @var data
 */
  public $data;

  /**
   * Is set when token is last token created by lexical analysis
   * @var last
 */
  public $last;
}

/**
* Class that identifies type of identifier
*
* @access public
*/
class tIdentifier {
  public $stringSearch;
  public $varSearch;
  public $numberSearch;
  public $labelSearch;
  public $markerSearch;
}

/**
* Class that identifies if arg statp is present
*
* @access public
*/
class aStatp {
  public $ispresent;
  public $stat_list;

  /**
  * Constains arguments given for gathering statistics
  * @var public
  */
  public $statistics;
}

/**
* Class that defines states of automaton and all possible token types
*
* @access public
*/
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

/**
 * Checks if help argument isn't present multiple times
 * @param argv  command line arguments
 * @param argc position of parsed argument
 * @return on error return exit code 10 else 0
 */
function arg_parse($argc, $argv){

  if($argc == 2 && ($argv[1] === "--help" || $argv[1] === "-help")){
      echo 'Usage: php7.3 parse.php | --help
            --help Prints help message'."\n";
      exit(0);
  }
  elseif($argc > 2 && $argv[1] === "--help"){
    fwrite(STDERR, "ERROR : ARGUMENTS : multiple use of --help argumet\n");
    exit(10);
  }
}

/**
 * Reads STDIN into array
 * @return returns array filled with stream from STDIN
 */
function read_stream(){
  global $array_stream;
  $array_key = 0;
  $array_stream = stream_get_contents(STDIN);
  $array_stream = str_split($array_stream);

  global $key_val;
  global $c_commentary;
  $c_commentary = 0;
  $key_val = 0;
}

/**
 * Creates indentifier object
 * @return new identifier object
 */
function preset_identifier()
{
  global $identifier;
  $identifier = new tIdentifier();
  $identifier->stringSearch = NULL;
  $identifier->varSearch = NULL;
  $identifier->numberSearch = NULL;
  $identifier->markerSearch = NULL;

}

/**
 * Creates label object
 * @return returns array filled with stream from STDIN
 */
function preset_label(){
  global $label;
  $label = new tIdentifier();
  $label->isset = NULL;
}

/**
 * Creates token
 * @return returns token used for analysis
 */
function init_token(){
  global $token;
  $token = new tToken();
  $token->data = NULL;
  $token->type = tokenType::start;
  $token->last = True;
}

/**
 * Searches for operand match in token
 */
function identify_operand(){
  global $token;
  global $identifier;
  global $label;
  switch ($token->data) {
    case 'string':
      $identifier->stringSearch = True;
      break;
    case 'int':
      $identifier->numberSearch = True;
      break;
    case '@':
      $identifier->markerSearch = True;
    default:
      if(preg_match("/^(LT)|(GT)|(LF)$/", $token->data)){
        $identifier->varSearch = True;
      }
      break;
  }
}
/**
 * Checks if any identifier is present in current operand.
 * Function changes type of operands which name is same as
 * keyword
 * @return proper operand type
 */
function isset_identif(){
  global $token;
  global $identifier;
  global $label;

  if($identifier->stringSearch && $identifier->markerSearch){
    $token->type = tokenType::stringStream;
  }
  elseif($identifier->varSearch){
    $token->type = tokenType::identifier;
    if(!preg_match("/^[a-zA-Z_\-\$&%\*!?][a-zA-Z_\-\$&%\*!?0-9]*$/", $token->data)){
      fwrite(STDERR,"ERROR : LEX : detected lexical error in: $token->data\n");
      exit(23);
    }
  }
  elseif($identifier->numberSearch && $identifier->markerSearch){
    $token->type = tokenType::number;
  }
  elseif($label->isset){
    $token->type = tokenType::identifier;
  }
}

/**
 * Parses array filled with STDIN and creates token.
 *
 * These contain data and proper token type. Through reading the array
 * function also checks lexical validity of given stream and
 * creates the token from it. Tokens are later used in syntax analysis
 * @return token with data and type from tokenType
 */
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
    /**
    * @warning end of Array works only for PHP7.3!!!!
    */
    if($key_val === array_key_last($array_stream)){
      $token->last = False;
    }
    /* State automaton for lexical analysis combined with usage of regular expressions */
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
          identify_operand();
          preset_label();
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
          preset_identifier();
        }
        elseif(ctype_alpha($array_stream[$key_val]) || ctype_digit($array_stream[$key_val]) || preg_match("/^_|\-|\$|&|%|\*|!|\?$/", $array_stream[$key_val])){
          $token_type = tokenType::charStream;
          break;
        }
        else {
          fwrite(STDERR, "ERROR : Input doesn't start with .IPPcode19 header\n");
          exit(21);#appropriate exit code
        }
        break;
      }
      case tokenType::header:
      {
        while(1){
          if($array_stream[$key_val] === PHP_EOL || preg_match("/^[ \t#]$/",$array_stream[$key_val])){
            if(preg_match("/^.ippcode19$/", strtolower($token->data))){
              $token->type = tokenType::header;
              $token_end = False;
              break;
            }
            else {
              fwrite(STDERR,"ERROR : Innapropriate header detected\n");
              exit(21);//no ippcode header;
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
        preset_label();
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
          if(preg_match("/^[ \t@]$/",$array_stream[$key_val])){         // === " " || $array_stream[$key_val] === "\t" || $array_stream[$key_val] === "@"){
            $token_type = tokenType::identifyStream;
            break;
          }
          elseif($array_stream[$key_val] === PHP_EOL || $array_stream[$key_val] === "#"){
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
          isset_identif();
          $token_end = False;
          break;
        }
        if(preg_match("/^[+|-]?[0-9]*$/", $token->data)){  //matching numbers   //^[+|-]?[1-9][0-9]*|[+|-][0]|[0]$
          $token->type = tokenType::number;
          $token_end = False;
          break;
        }
        elseif(preg_match("/^([\x{0024}-\x{005B}]|[\x{0021}\x{0022}]|[\x{005D}-\x{FFFF}]|[ěščřžýáíéóúůďťňĎŇŤŠČŘŽÝÁÍÉÚŮa-zA-Z0-9]|([\\\\][0-9]{3})?)*$/", $token->data)){   //^([ěščřžýáíéóúůďťňĎŇŤŠČŘŽÝÁÍÉÚŮa-zA-Z0-9]|([\\\\][0-9]{3})?)*$
          $token->type = tokenType::stringStream;
          $token_end = False;
        }
        else {
          fwrite(STDERR,"ERROR : LEX : detected lexical error in: $token->data\n");
          exit(23);
        }
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
preset_label();
init_token();

/*  Header occurence check*/
get_token();
if($token->type === tokenType::header)
{
  get_token();
  if($token->type !== tokenType::EOL){
    fwrite(STDERR, "ERROR : HEADER : Header must be followed by new line\n");
    exit(23);
  }
}
else{
  fwrite(STDERR, "ERROR : HEADER : Missing header in format .ippcode19\n");
  exit(21);
}
$header_check = 1;

/**
 * Checks if string contains problematic characters
 *
 * Any problematic character for xml is replaced with it's
 * XML friendly format
 * @param t_data string chain
 * @return string chain without problematic characters
 */
function xml_special_char($t_data){

  if(preg_match("/\"/", $t_data)) str_replace("\"", "&quot", $t_data);
  elseif(preg_match("/'/", $t_data)) str_replace("\'", "&quot", $t_data);
  elseif(preg_match("/&/", $t_data)) str_replace("&", "&amp", $t_data);
  elseif(preg_match("/</", $t_data)) str_replace("<", "&lt", $t_data);
  elseif(preg_match("/>/", $t_data)) str_replace(">", "&gt", $t_data);

  return $t_data;
}

/**
 * Seaches for keyword appearance in current token
 * @param type type of keyword which will be assigned on match
 * @return proper operand type
 */
function is_keyword($type){
  global $keywords;
  global $token;

  foreach ($keywords as $key => $value) { //searching for keyword
    $match_pattern = "/\b" . "$value" . "\b/i";
    if(preg_match($match_pattern, strtolower($token->data))){
      $token->type = $type;
      return True;
    }
  }
  return False;
}

/***************************************************************************************
*
*                  SYNTAX ANALYSIS AND GENERATION OF XML OUTPUT
*
***************************************************************************************/

/**
 * Seaches for EndOfLine after each instruction of IPPcode19
 * @return error code 22 on EOL missing
 */
function eol_identify(){
  global $token;

  get_token();
  if($token->type !== tokenType::EOL){
    fwrite(STDERR, "ERROR : SYNTAX : End of line <eol> expected : last token: $token->data\n");
    exit(22);
  }
}

/**
 * Scans given token data for proper case sensitivity
 * @param t_data token data
 * @param mode is set to 1 only if the search is for boolean values
 * @return error code 23 on lexical error
 */
function upper_scan($t_data, $mode){
  if(!$mode){
    switch ($t_data) {
      case 'int':
      case 'string':
      case 'nil':
      case 'bool':
      case 'LF':
      case 'GF':
      case 'TF':
      break;

      default:
        fwrite(STDERR, "ERROR : LEX : Wrong case sensitivity detected in $t_data\n");
        exit(23); #lex error
      break;
    }
  }
  else {
    if(!preg_match("/^(true)|(false)$/", $t_data)){
      fwrite(STDERR, "ERROR : LEX : Wrong case sensitivity detected in $t_data\n");
      exit(23);
    }
  }
}

/**
 * Tries to identify variable in token stream

 * Function is called after occurence of instruction which is
 * using operands of type <var>. It tries to apply rules for
 * proper <var> syntax. Function also generates XML element.
 * @param arg1 defines element of XML for instuct. element
 * @return instruction element of root XML element
 */
function var_identify($arg1){
  global $token;
  $error_val = False;

  get_token();
  if($token->type >= tokenType::f_gf && $token->type <= tokenType::f_tf){
    upper_scan($token->data, 0);
    $arg1->addAttribute('type', 'var');
    $arg1[0] = $token->data;
    get_token();
    if($token->type === tokenType::marker){
      $arg1[0] .= $token->data;
      get_token();
      if($token->type !== tokenType::identifier){
        if(!preg_match("/^[a-zA-Z_\-\$&%\*!?][a-zA-Z_\-\$&%\*!?0-9]*$/", $token->data)){
          fwrite(STDERR,"ERROR : LEX : detected lexical error in: $token->data\n");
          exit(23);
        }
        if(!is_keyword(tokenType::identifier)){
          $error_val = True;
        }
      }
      $arg1[0] .= $token->data;
    }
    else $error_val = True;
  }
  else $error_val = True;

  if($error_val){
    fwrite(STDERR, "ERROR : SYNTAX : Variable <var> expected : last token: $token->data  $token->type\n");
    exit(22);
  }
}
/**
 * Tries to identify symbol in token stream

 * Function is called after occurence of instruction which is
 * using operands of type <symb>. It tries to apply rules for
 * proper <symb> syntax. Function also generates XML element.
 * @param arg_order defines element of XML for instuct. element
 * @return instruction element of root XML element
 */
function symb_identify($arg_order){
  global $token;
  $error_val = False;

  get_token();
  if($token->type === tokenType::d_int){
    upper_scan($token->data, 0);
    $arg_order->addAttribute('type','int');
    get_token();
    if($token->type === tokenType::marker){
      get_token();
      if($token->type !== tokenType::number){
        $error_val = True;
      }
      $arg_order[0] .= $token->data;
    }
    else $error_val = True;
  }
  elseif($token->type === tokenType::d_string){
    upper_scan($token->data, 0);
    $arg_order->addAttribute('type','string');
    get_token();
    if($token->type === tokenType::marker){
      get_token();
      if($token->type !== tokenType::stringStream){
        if(preg_match("/^[+|-]?[0-9]*$/",$token->data)){
          $token->type === tokenType::number;
        }
        else {
          $error_val = True;
        }
      }
      $arg_order[0] .= xml_special_char($token->data);
    }
    else $error_val = True;
  }
  elseif($token->type === tokenType::d_bool){
    upper_scan($token->data, 0);
    $arg_order->addAttribute('type','bool');
    get_token();
    if($token->type === tokenType::marker){
      get_token();
      upper_scan($token->data, 1);
      if($token->type === tokenType::b_true){
        $arg_order[0] .= $token->data;
      }
      elseif($token->type === tokenType::b_false){
        $arg_order[0] .= $token->data;
      }
      else $error_val = True;
    }
    else $error_val = True;
  }
  elseif($token->type === tokenType::d_nil){
    upper_scan($token->data, 0);
    $arg_order->addAttribute('type', 'nil');
    get_token();
    if($token->type === tokenType::marker){
      get_token();
      upper_scan($token->data, 0);
      if($token->type !== tokenType::d_nil){
        $error_val = True;
      }
      $arg_order[0] .= $token->data;
    }
    else $error_val = True;
  }
  elseif($token->type >= tokenType::f_gf && $token->type <= tokenType::f_tf){
    upper_scan($token->data, 0);
    $arg_order->addAttribute('type', 'var');
    $arg_order[0] .= $token->data;
    get_token();
    if($token->type === tokenType::marker){
      $arg_order[0] .= $token->data;
      get_token();
      if(!preg_match("/^[a-zA-Z_\-\$&%\*!?][a-zA-Z_\-\$&%\*!?0-9]*$/", $token->data)){
        fwrite(STDERR,"ERROR : LEX : detected lexical error in: $token->data\n");
        exit(23);
      }
      if($token->type !== tokenType::identifier){
        $error_val = True;
      }
      $arg_order[0] .= xml_special_char($token->data);
    }
    else $error_val = True;
  }
  else $error_val = True;

  if($error_val){
    fwrite(STDERR, "ERROR : SYNTAX : Symbol <symb> expected : last token: $token->data  $token->type\n");
    exit(22);
  }
}

$v_statp = new aStatp();
$v_statp->ispresent = 0;
$v_statp->stat_list = [];
$statp_stats[1] = 0;
$statp_stats[2] = 0;
$statp_stats[3] = 0;

$program = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?>'.'<program></program>');  //creating SimpleXML object
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
  /*  State automaton for syntax analysis */
  switch ($token->type) {
    case tokenType::header:
          eol_identify();
          $header_check++;
          $statp_stats[1]--;
          break;
    case tokenType::i_createframe:
    case tokenType::i_pushframe:
    case tokenType::i_popframe:
    case tokenType::i_return:
    case tokenType::i_break:
          eol_identify();
          break;
    case tokenType::i_label:
          $statp_stats[2]++;
    case tokenType::i_call:
    case tokenType::i_jump:
          $arg1 = $instruction->addChild('arg1');
          $arg1->addAttribute('type', 'label');
          get_token();
          if($token->type !== tokenType::identifier){
            if(!is_keyword(tokenType::identifier)){
              fwrite(STDERR, "ERROR : SYNTAX : Label <label> expected : last token: $token->data  $token->type\n");
              exit(22);
            }
          }
          $arg1[0] .= $token->data;
          if($token->type === tokenType::i_jump) $statp_stats[3]++; // || $token->type === tokenType::i_call
          eol_identify();
          break;
    case tokenType::i_defvar:
    case tokenType::i_pops:
          $arg1 = $instruction->addChild('arg1');
          var_identify($arg1);
          eol_identify();
          break;
    case tokenType::i_pushs:
    case tokenType::i_write:
    case tokenType::i_exit:
    case tokenType::i_dprint:
          $arg1 = $instruction->addChild('arg1');
          symb_identify($arg1);
          eol_identify();
          break;
    case tokenType::i_move:
    case tokenType::i_int2char:
    case tokenType::i_strlen:
    case tokenType::i_type:
    case tokenType::i_not:
          $arg1 = $instruction->addChild('arg1');
          $arg2 = $instruction->addChild('arg2');
          var_identify($arg1);
          symb_identify($arg2);
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
          $arg1 = $instruction->addChild('arg1');
          $arg2 = $instruction->addChild('arg2');
          $arg3 = $instruction->addChild('arg3');
          var_identify($arg1);
          symb_identify($arg2);
          symb_identify($arg3);
          eol_identify();
          break;
    case tokenType::i_jumpifeq:
    case tokenType::i_jumpifneq:
          $arg1 = $instruction->addChild('arg1');
          $arg2 = $instruction->addChild('arg2');
          $arg3 = $instruction->addChild('arg3');
          $arg1->addAttribute('type', 'label');
          get_token();
          if($token->type !== tokenType::identifier){
            if(!is_keyword(tokenType::identifier)){
              fwrite(STDERR, "ERROR : SYNTAX : Expected <label> : last token: $token->data   $token->type\n");
              exit(22);
            }
          }
          $arg1[0] .= $token->data;
          symb_identify($arg2);
          symb_identify($arg3);
          eol_identify();
          $statp_stats[3]++;
          break;
    case tokenType::i_read:
          $arg1 = $instruction->addChild('arg1');
          var_identify($arg1);
          get_token();
          if($token->type < tokenType::d_string || $token->type > tokenType::d_bool){
            fwrite(STDERR, "ERROR : SYNTAX : Expected <type> : last token: $token->data  $token->type\n");
            exit(22);
          }
          $arg2 = $instruction->addChild('arg2');
          $arg2->addAttribute('type', 'type');
          $arg2[0] .= $token->data;
          break;
    case tokenType::EOL:
          $statp_stats[1]--;
          break;
    default:
      fwrite(STDERR, "ERROR : INSTRUCTION : Unknown instruction detected $token->data\n");
      exit(22); ##2
      break;
  }
}

/*  Transforming SimpleXML to DOM and removing white space for nice formatting */
$dom = new DOMDocument("1.0");  //creating DOM object
$dom->preserveWhiteSpace = false;
$dom->formatOutput = true;
$dom->loadXML($program->asXML()); //loading SimpleXML to DOM
echo $dom->saveXML(); //printing DOM


if($header_check != 1){ //header is not present or has been found multiple times
  fwrite(STDERR, "ERROR : HEADER : Multiple headers detected\n");
  exit(22); ##22
}

/*  Parsing arguments for statp */
foreach ($argv as $key => $value) {
  if(preg_match("/(\-\-stats=)|(\-\-loc)|(\-\-comments)|(\-\-labels)|(\-\-jumps)/",$argv[$key])){
    array_push($v_statp->stat_list, $argv[$key]);
    if(preg_match("/(\-\-stats=)/", $argv[$key])){
      array_pop($v_statp->stat_list);
      $file_stat = substr($argv[$key], 8); //file name
      if(!file_exists($file_stat)){
        if(!is_readable($file_stat)){
          $file_stat = fopen("$file_stat", "w+");
          // fclose($file_stat);
          if(!$file_stat){
            fwrite(STDERR, "ERROR : FILE : couldn't open file\n");
            exit(12);
          }
        }
      }
      $v_statp->ispresent++;
    }
  }
  elseif(preg_match("/(parse.php)/", $argv[$key])){
      array_pop($v_statp->stat_list);
  }
  else {
    fwrite(STDERR, "ERROR : ARGUMENTS : unknown argument $value use --help\n");
    exit(10);
  }
}
/*
 * Multiple occurence of argument --statp or occurence of
 * --loc or --jumps or --labels or --comments without usage of --statp
*/
if($v_statp->ispresent !== 1 && !empty($v_statp->stat_list)){
  fwrite(STDERR, "ERROR : STATP : --stats not present\n");
  exit(10);
}
elseif($v_statp->ispresent === 1) file_put_contents($file_stat, "");  //clear file contents

foreach ($v_statp->stat_list as $key => $value) { //saving statistics to file
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
/* EOF */
 ?>
