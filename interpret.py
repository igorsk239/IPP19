import xml.etree.ElementTree as elem_tree
from io import StringIO
import sys
import re
import os

#dict print only
import pprint


# TODO read from stdin not only from file

class Args:
    def __init__(self, p_source, p_input):
        self.source = p_source
        self.input = p_input
    def set_source(self, p_source):
        self.source = p_source
    def set_input(self, p_input):
        self.input = p_input
    def get_attrib(self):
        return (self.source, self.input)


class Instruction:
    def __init__(self, Instruction):
        self.name = (Instruction.attrib).get('opcode')
        self.arg1 = Instruction.find('arg1')
        self.arg2 = Instruction.find('arg2')
        self.arg3 = Instruction.find('arg3')

        if self.arg1 is not None:
            self.arg1Val = {self.arg1.attrib.get('type'): self.arg1.text}
            # pprint.pprint(self.arg1Val)
        else:
            self.arg1Val = {None: None}

        if Instruction.find('arg2') is not None:
            self.arg2Val = {self.arg2.attrib.get('type'): self.arg2.text}
            # pprint.pprint(self.arg2Val)
        else:
            self.arg2Val = {None: None}

        if self.arg3 is not None:
            self.arg3Val = {self.arg3.attrib.get('type'): self.arg3.text}
            # pprint.pprint(self.arg3Val)
        else:
            self.arg3Val = {None: None}
        # sys.stdout.write("args:\n%s\n%s\n%s\n" %(self.arg1, self.arg2, self.arg3))

    def get_instr_name(self):
        return self.name
    def get_instr_args(self):
        return (self.arg1, self.arg2, self.arg3)
    def get_arg_val(self):
        return (self.arg1Val, self.arg2Val, self.arg3Val)


def parse_xml(tree_ptr):
    root = tree_ptr.getroot()

    if root.tag != "program":
        sys.stderr.write("ERROR: wrong formatting of root element expected: %s\n" %root.tag)
        exit()
    if root.attrib.get('language') != "IPPcode19":
        sys.stderr.write("ERROR: wrong formatting of root element expected: %s attribute\n" %root.attrib)
        exit()
    return root

# Functions for lexical analysis of given instruction operands
def parse_var(op_val):
    if re.search('GF@|LF@|TF@', op_val[:3]) is None:
        sys.stderr.write("ERROR : lexical error in given stream : %s frame expected\n" %op_val[:3])
        exit()
    if re.search('^[a-zA-Z_\-\$&%\*!?][a-zA-Z_\-\$&%\*!?0-9]*$', op_val[3:]) is None:
        sys.stderr.write("ERROR : lexical error in given stream : %s identifier expected\n" %op_val)
        exit()

def parse_int(op_val):
    if re.search('^[+|-]?[1-9][0-9]*|[+|-][0]|[0]$', op_val) is None:
        sys.stderr.write("ERROR : lexical error in given stream : %s <int> expected\n" %op_val)
        exit()

def parse_string(op_val):
    if re.search('^([\u0024-\u005B]|[\u0021\u0022]|[\u005D-\uFFFF]|[ěščřžýáíéóúůďťňĎŇŤŠČŘŽÝÁÍÉÚŮa-zA-Z0-9]|([\\\\][0-9]{3})?)*$', op_val) is None:
        sys.stderr.write("ERROR : lexical error in given stream : %s <string> expected\n" %op_val)
        exit()

def parse_bool(op_val):
    if re.search('false|true', op_val) is None:
        sys.stderr.write("ERROR : lexical error in given stream : %s <bool> expected\n" %op_val)
        exit()

def parse_nil(op_val):
    if re.search('nil', op_val) is None:
        sys.stderr.write("ERROR : lexical error in given stream : %s <nil> expected\n" %op_val)
        exit()

def parse_label(op_val):
    if re.search('^[a-zA-Z_\-\$&%\*!?][a-zA-Z_\-\$&%\*!?0-9]*$', op_val) is None:
        sys.stderr.write("ERROR : lexical error in given stream : %s <label> expected\n" %op_val)
        exit()

def parse_type(op_val):
    if re.search('int|string|bool', op_val) is None:
        sys.stderr.write("ERROR : lexical error in given stream : %s <type> expected\n" %op_val)
        exit()

def syntax_check(instr_name):
    instr_opcodes = (
        "move", "createframe", "pushframe", "popframe", "defvar", "call", "return",
        "pushs", "pops",
        "add", "sub", "mul", "idiv", "lt", "gt", "eq", "and", "or", "not", "int2char", "stri2int",
        "read", "write",
        "concat", "strlen", "getchar", "setchar",
        "type",
        "label", "jump", "jumpifeq", "jumpifneq", "exit",
        "dprint", "break"
    )

    for key_word in instr_opcodes:
        if key_word == instr_name:
            # OK


# Argument parse
arg_parse = Args("None", "None")

if len(sys.argv) == 1:
    sys.stderr.write("ERROR : ARGUMENTS : need argument --source of --input run --help\n")
    exit()
elif sys.argv[1] == "--help" and len(sys.argv) < 3:
    print("Help message");
    exit(0);

if len(sys.argv) > 3:
    sys.stderr.write("ERROR : ARGUMENTS : too many arguments run --help for further info\n")
    exit()

if len(sys.argv) == 3:
    if re.search('^(--source=)+', sys.argv[1]) and re.search('^(--input=)+', sys.argv[2]):
        print("both1")
        print(sys.argv[1])
        arg_parse.set_source((sys.argv[1])[9:])
        arg_parse.set_input((sys.argv[2])[8:])
    elif re.search('^(--input=)+', sys.argv[1]) and re.search('^(--source=)+', sys.argv[2]):
        print("both2")
        arg_parse.set_input((sys.argv[1])[8:])
        arg_parse.set_source((sys.argv[2])[9:])
    else:
        sys.stderr.write("ERROR : ARGUMENTS : unknown arguments run --help for further info\n")
elif len(sys.argv) == 2:
    if re.search('^(--source=)+', sys.argv[1]):
        print("source")
        arg_parse.set_source((sys.argv[1])[9:])
    elif re.search('^(--input=)+', sys.argv[1]):
        print("input")
        arg_parse.set_input((sys.argv[1])[8:])
    else:
        sys.stderr.write("ERROR : ARGUMENTS : unknown arguments run --help for further info\n")
        exit()

if((arg_parse.get_attrib())[0] != "None"):
    source_file_name = (arg_parse.get_attrib())[0]

    try:
        if not os.access(source_file_name, os.R_OK):
            sys.stderr.write("ERROR : FILE : could not read from file - weak permissions\n")
            exit()
        source_file = open(source_file_name, "r")

    except FileNotFoundError:
        sys.stderr.write("ERROR : FILE : given file does not exists\n")
        exit()
    except elem_tree.ParseError:
        sys.stderr.write("ERROR : XML : XML file is not well-formed\n")
        exit()

    source_xml = ""
    for line in source_file:
        source_xml = source_xml + line

else:
    source_xml = ""
    for line in sys.stdin:
        source_xml = source_xml + line


try:
    xml_file = elem_tree.fromstring(source_xml)

except elem_tree.ParseError:
    sys.stderr.write("ERROR : XML : XML file is not well-formed\n")
    exit()


tree = elem_tree.parse(source_file_name)
root = parse_xml(tree)
instruct_list = list()

# parse given XML and create obj for every instruction
for instr in root.iter('instruction'):
    act = Instruction(instr)
    instruct_list.append(act)   # insert all instructions into list

# loop over instruction list
for instr in instruct_list:

    args = instr.get_arg_val()
    # syntax_check() -----------------------------------------
    # loop over tuple of instruction's arguments
    for arg_n in args:
        # loop over dictionary == arg values
        for i_type, i_val in arg_n.items():

            if i_type == 'var' or i_type == 'label':
                parse_var(i_val)
            elif i_type == 'int':
                parse_int(i_val)
            elif i_type == 'string':
                parse_string(i_val)
            elif i_type == 'bool':
                parse_bool(i_val)
            elif i_type == 'nil':
                parse_nil(i_val)
            elif i_type == 'label':
                parse_label(i_val)
            elif i_type == 'type':
                parse_type(i_val)
            elif i_type is None:
                pass
            else:
                sys.stderr.write("ERROR : Unknown argument type: %s of instruction %s\n" %(i_type, instr.get_instr_name()))
                exit()
