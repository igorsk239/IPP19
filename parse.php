<?php

$keywords = array(
  "move", "createframe", "pushframe", "popframe", "defvar", "call", "return",
  "pushs", "pops",
  "add", "sub", "mul", "idiv", "lt", "gt", "eq", "and", "or", "not", "int2char", "stri2int",
  "read", "write",
  "concat", "strlen", "getchar", "setchar",
  "type",
  "label", "jump", "jumpifeq", "jumpifneq", "exit",
  "dprint", "break"
);
class tToken {
  public $type;
  public $data;
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

  const identifier = 200;
  const number = 201;
}

function arg_parse($argc, $argv){

  if($argc === 1){
    ;
  }
  elseif($argc == 2 && ($argv[1] === "--help" || $argv[1] === "-help")){
      echo 'Usage: php7.3 parse.php | --help
            --help Prints help message'."\n";
  }
  else{
    fwrite(STDERR, "Usage of innapropriate argumets run parse.php --help for further details\n");
    exit(); //appropriate exit code
  }
}

function read_stream(){
  global $array_stream;
  $array_key = 0;

  while($character = fgetc(STDIN)){
    $array_stream[$array_key] = $character;
    $array_key++;
  }
  global $key_val;
  $key_val = 0;
}

function init_token(){
  global $token;
  $token = new tToken();
  $token->data = NULL;
  $token->type = tokenType::start;
}

function get_token(){
  global $token;
  global $array_stream;
  global $key_val;
  global $keywords;
  $token_end = True;
  $token_type = tokenType::start;
  init_token();

  while($token_end){
    //if($array_stream[$key_val] === end($array_stream))  break;  //end of Array !!!!

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
        $token_end = False;
        break;
      }
      case tokenType::commentary:
      {
        while($array_stream[$key_val] !== PHP_EOL)
        {
          $key_val++;
        }
        $key_val--;
        $token_end = False;
        break;
      }
      case tokenType::charStream:
      {
        while(1){
          if($array_stream[$key_val] === " " || $array_stream[$key_val] === "\t"){
            $token_type = tokenType::identifyStream;
            break;
          }
          elseif($array_stream[$key_val] === PHP_EOL){
            $token_type = tokenType::identifyStream;
            $key_val--;
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
              break;
            }
          }
          $token_end = False;
          break;
        }
        if(preg_match("/^[+|-]?[1-9][0-9]*|[+|-][0]|[0]$/", $token->data)){  //matching numbers
          $token->type = tokenType::number;
          $token_end = False;
          break;
        }
        else {
          fwrite(STDERR,"ERROR : LEX : detected\n");
          exit();//no ippcode header;
        }


      }

      default:
        # code...
        break;
    }
  }
}

arg_parse($argc, $argv);
read_stream();

get_token();
echo "token data: " . $token->data . " type: " . $token->type . "\n";
get_token();
echo "token data: " . $token->data . " type: " . $token->type . "\n";
get_token();
echo "token data: " . $token->data . " type: " . $token->type . "\n";
get_token();
echo "token data: " . $token->data . " type: " . $token->type . "\n";
get_token();
echo "token data: " . $token->data . " type: " . $token->type . "\n";
get_token();
echo "token data: " . $token->data . " type: " . $token->type . "\n";
get_token();
echo "token data: " . $token->data . " type: " . $token->type . "\n";
get_token();
echo "token data: " . $token->data . " type: " . $token->type . "\n";
get_token();
 ?>
