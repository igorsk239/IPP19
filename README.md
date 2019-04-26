# IPP19

# Parser
    Usage: php7.3 test.php | --help | [--stats=file] [--loc] | [--comments] | [--labels] | [--jumps]
              Parser for .IPPcode19 language\n
                --help        help message
                --stats=file  file which will contain code statistics
                --loc         statistic for lines of code present in source file
                --comments    statistic for commentaries present in source code
                --labels      statistic for labels in source code
                --jumps       statistic for jump instructions in source cod

    Parse will parse given input from STDIN and checks it lexical and syntax correctness.
    Through analysis parser also generates XML file as output to STDOUT. XML file consists
    of instructions and their operands writen in XML standard.
      

# Interpet
    Interpret of language .IPPcode19 written in XML format.
    
    Usage: python3 interpret.py --help | [--input=path | --source=path]
            
               --help          prints help message
               --input=path    specifies path to input file for IPPcode19 instructions
               --source=path   specifies path to source code file of IPPcode19
           
    Interpret checks given XML input and control lexical, syntax and semantic of given code.
    
# Test
    Usage: php7.3 test.php | --help | [--directory=path] [--recursive] [--parse-script=file] [--int-script=file] | [--parse-only] | [--int-only]
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
    succession to STDIN.
