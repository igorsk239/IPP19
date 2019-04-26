##
# @file: interpret.py
# @author: Igor Ignác xignac00@fit.vutbr.cz
# @name: Implementation of Project for IPP 2018/2019
# @date 11.2.2019
# Faculty: Faculty of Information Technology, Brno University of Technology
##


import xml.etree.ElementTree as elem_tree
from io import StringIO
import sys
import re
import os

# GF global frame structured as dictionary
global_frame = []
# Data stack used by stack instructions
data_stack = []
# Stack used for storage of position of intern counter
call_stack = []
# List of labels present in source code
labels = []

## Class used for storing program arguments
class Args:
    def __init__(self, p_source, p_input):
        self.source = p_source
        self.input = p_input
    ## On argument occurence filling class attributes
    def set_source(self, p_source):
        self.source = p_source
    def set_input(self, p_input):
        self.input = p_input
    ## Retrieving prog arguments
    def get_attrib(self):
        return (self.source, self.input)

## Used for source code variables
#
# Class used for <var> type. Able to store name, frame and value of variable
class Variable:
    def __init__(self, name):
        self.name = name
        self.value = None
    ## Filling
    def set_value(self, value, op_type):
        self.value = value;
        self.type = op_type
    ## Retrieve information
    def get_value(self):
        return self.value
    def get_type(self):
        return self.type
    def get_name(self):
        return self.name

## Represents one intruction retrieved from xml file
#
# Used for modifying and storing all information about given Instruction
class Instruction:
    # Fill Instruction information
    def __init__(self, Instruction):
        self.name = (Instruction.attrib).get('opcode')
        self.line = (Instruction.attrib).get('order')    # position line in xml
        self.arg1 = Instruction.find('arg1')
        self.arg2 = Instruction.find('arg2')
        self.arg3 = Instruction.find('arg3')

        if self.arg1 is not None:
            self.arg1Val = {self.arg1.attrib.get('type'): self.arg1.text}

        else:
            self.arg1Val = {None: None}

        if Instruction.find('arg2') is not None:
            self.arg2Val = {self.arg2.attrib.get('type'): self.arg2.text}

        else:
            self.arg2Val = {None: None}

        if self.arg3 is not None:
            self.arg3Val = {self.arg3.attrib.get('type'): self.arg3.text}

        else:
            self.arg3Val = {None: None}

    def get_instr_name(self):
        return self.name

    def get_instr_pos(self):
        return self.line
    # Returns all instruction arguments
    def get_instr_args(self):
        return (self.arg1, self.arg2, self.arg3)
    # Return only instruction arguments values
    def get_arg_val(self):
        return (self.arg1Val, self.arg2Val, self.arg3Val)
    # Return number of arguments present in Instruction
    def get_arg_total(self):
        t_arg = self.get_arg_val()
        arg_sum = 0
        for arg in t_arg:
            for arg_val in arg:
                if arg_val is not None:
                    arg_sum += 1
        return arg_sum
    # Retrieve specify argument value
    def get_specific_arg(self, position):
        if position == 1:
            return self.arg1Val
        elif position == 2:
            return self.arg2Val
        elif position == 3:
            return self.arg3Val
        else:
            raise ValueError('Unknown position number in method get_specific_arg\n')
    # Updating value of argument - mainly used for variable objects
    def update_val(self, arg, new_val):
        for i_arg in self.get_arg_val():
            if arg is self.arg1Val:
                for key, value in self.arg1Val.items():
                    self.arg1Val[key] = new_val
            elif arg is self.arg2Val:
                for key, value in self.arg2Val.items():
                    self.arg2Val[key] = new_val
            elif arg is self.arg3Val:
                for key, value in self.arg3Val.items():
                    self.arg3Val[key] = new_val

## Functions for XML parsing
#
# Checks if given xml file is well-formed
# @param tree_ptr root of xml retrieved from ElementTree
def parse_xml(tree_ptr):
    root = tree_ptr.getroot()

    if root.tag != "program":   # Necessary element
        sys.stderr.write("ERROR: wrong formatting of root element expected: %s\n" %root.tag)
        exit(32)
    if root.attrib.get('language') != "IPPcode19":  # Defines language of code written into xml
        sys.stderr.write("ERROR: wrong formatting of root element expected: %s attribute\n" %root.attrib)
        exit(32)
    return root

## Functions for lexical analysis of given instruction operands
#
# Multiple function used for parsing multiple types. All of them are using
# regular expression trying to match desired format.
# @param op_val value of string we test
def parse_var(op_val):
    if re.search('GF@|LF@|TF@', op_val[:3]) is None:
        sys.stderr.write("ERROR : LEXICAL error in given stream : %s frame expected\n" %op_val[:3])
        exit(32)
    if re.search('^[a-zA-Z_\-\$&%\*!?][a-zA-Z_\-\$&%\*!?0-9]*$', op_val[3:]) is None:
        sys.stderr.write("ERROR : LEXICAL error in given stream : %s identifier expected\n" %op_val)
        exit(32)

def parse_label(op_val):
    if re.search('^[a-zA-Z_\-\$&%\*!?][a-zA-Z_\-\$&%\*!?0-9]*$', op_val) is None:
        sys.stderr.write("ERROR : LEXICAL error in given stream : %s identifier expected\n" %op_val)
        exit(32)

def parse_int(op_val):
    if re.search('^[+|-]?[1-9][0-9]*|[+|-][0]|[0]$', op_val) is None:
        sys.stderr.write("ERROR : LEXICAL error in given stream : %s <int> expected\n" %op_val)
        exit(32)

def parse_string(op_val):
    if op_val is None:
        return ''
    if re.search('^([\u0024-\u005B]|[\u0021\u0022]|[\u005D-\uFFFF]|[ěščřžýáíéóúůďťňĎŇŤŠČŘŽÝÁÍÉÚŮa-zA-Z0-9]|([\\\\][0-9]{3})?)*$', op_val) is None:
        sys.stderr.write("ERROR : LEXICAL error in given stream : %s <string> expected\n" %op_val)
        exit(32)
    else:
        # Convert escape sequences to unicode character
        matches = re.findall('[\\\\][0-9]{3}', op_val)
        if len(matches) != 0 :
            for m in matches:
                # Replace
                op_val = op_val.replace(m , chr(int(m[1:])))
        return op_val

def parse_bool(op_val):
    if re.search('false|true', op_val) is None:
        sys.stderr.write("ERROR : LEXICAL error in given stream : %s <bool> expected\n" %op_val)
        exit(32)

def parse_nil(op_val):
    if re.search('nil', op_val) is None:
        sys.stderr.write("ERROR : LEXICAL error in given stream : %s <nil> expected\n" %op_val)
        exit(32)

def parse_label(op_val):
    if re.search('^[a-zA-Z_\-\$&%\*!?][a-zA-Z_\-\$&%\*!?0-9]*$', op_val) is None:
        sys.stderr.write("ERROR : LEXICAL error in given stream : %s <label> expected\n" %op_val)
        exit(32)

def parse_type(op_val):
    if re.search('int|string|bool', op_val) is None:
        sys.stderr.write("ERROR : LEXICAL error in given stream : %s <type> expected\n" %op_val)
        exit(32)

################################################################################

## Functions for syntax analysis
#
# @param instr element retrieved from ElementTree
# @param exp expected number of arguments
# @return true on success
def arg_count(instr, exp):

    if instr.get_arg_total() != exp:
        sys.stderr.write("ERROR : SYNTAX Wrong number of arguments in %s expected %d\n" %(instr.get_instr_name(), exp))
        exit(32)
    else:
        return True

## Checks for supported data type
#
# @param op_val string representing data type
# @return true on success
def is_symbol(op_val):

    b_symb = False

    if op_val == 'int':
        b_symb = True
    elif op_val == 'string':
        b_symb = True
    elif op_val == 'bool':
        b_symb = True
    elif op_val == 'nil':
        b_symb = True
    elif op_val == 'var':
        b_symb = True

    return b_symb

## Searches in array of keywords
#
# Function checks if given instr has valid number of arguments.
# Number of arguments depends on its position in array
# @param instr given instruction
# @param position which defines number of expected arguments
def syntax_struct(instr, instr_number):

    instr_args = instr.get_arg_val()  # all arguments of instruction

    if 1 <= instr_number <= 5:
        # if instr_args.count(None) != len(instr_args):
        if instr.get_arg_total() != 0:
            sys.stderr.write("ERROR : SYNTAX Unknown operand in instruction: %s\n" %instr.get_instr_name())
            exit(32)

    elif 6 <= instr_number <= 8:
        if instr.get_arg_total() != 1 or next(iter(instr_args[0])) != 'label':
            sys.stderr.write("ERROR : SYNTAX Wrong number of arguments or argument type in %s\n" %instr.get_instr_name())
            exit(32)

    elif 9 <= instr_number <= 10:
        if instr.get_arg_total() != 1 or next(iter(instr_args[0])) != 'var':
            sys.stderr.write("ERROR : SYNTAX Wrong number of arguments or argument type in %s\n" %instr.get_instr_name())
            exit(32)

    elif 11 <= instr_number <= 14:
        arg_count(instr, 1)
        if not is_symbol(next(iter(instr_args[0]))):
            sys.stderr.write("ERROR : SYNTAX Wrong type of argument in %s\n" %instr.get_instr_name())
            exit(32)

    elif 15 <= instr_number <= 19:
        arg_count(instr, 2)
        if next(iter(instr_args[0])) != 'var' or not is_symbol(next(iter(instr_args[1]))):
            sys.stderr.write("ERROR : SYNTAX Wrong type of argument in %s\n" %instr.get_instr_name())
            exit(32)

    elif 20 <= instr_number <= 32:
        arg_count(instr, 3)
        if next(iter(instr_args[0])) != 'var' or not is_symbol(next(iter(instr_args[1]))) or not is_symbol(next(iter(instr_args[2]))):
            sys.stderr.write("ERROR : SYNTAX Wrong type of argument in %s\n" %instr.get_instr_name())
            exit(32)

    elif 33 <= instr_number <= 34:
        if next(iter(instr_args[0])) != 'label' or not is_symbol(next(iter(instr_args[1]))) or not is_symbol(next(iter(instr_args[2]))):
            sys.stderr.write("ERROR : SYNTAX Wrong type of argument in %s\n" %instr.get_instr_name())
            exit(32)

    elif instr_number == 35:
        arg_count(instr, 2)
        if instr_args[0].get('var') is None or instr_args[1].get('type') is None:
            sys.stderr.write("ERROR : SYNTAX Wrong type of argument in %s\n" %instr.get_instr_name())
            exit(32)

## Start point for syntax analysis
#
# Creates array of key-val elements, where position defines required number of arguments
# @param instr analysed instruction
def syntax_check(instr):
    instr_opcodes = {
        "createframe": 1, "pushframe": 2, "popframe": 3, "return": 4, "break": 5,
        "label": 6, "jump": 7, "call": 8,
        "defvar": 9, "pops": 10,
        "pushs": 11, "write": 12,"exit": 13, "dprint": 14,
        "move": 15, "int2char": 16, "strlen": 17, "type": 18, "not": 19,
        "add": 20, "sub": 21, "mul": 22, "idiv": 23, "lt": 24, "gt": 25, "eq": 26, "and": 27, "or": 28, "stri2int": 29, "concat": 30,  "getchar": 31, "setchar": 32,
        "jumpifeq": 33, "jumpifneq": 34,
        "read": 35
    }

    op_code = instr.get_instr_name()

    # loop over keywords to find if instr exists
    found = False
    for key_word, instr_number in instr_opcodes.items():
        if key_word.upper() == op_code.upper():
            found = True
            break
    if not found:
        sys.stderr.write("ERROR : INSTRUCTION unknown name of instruction : %s\n" %op_code)
        exit(32)

    syntax_struct(instr, instr_number)
################################################################################

## Function only used for variables
#
# All variables passed are checked for their existence in frame. Examined frame
# is defined by instr name - LF for local frame, GF for global frame etc.
# @var examined variable
# @instr instruction containing given variable - used only for error message
def var_is_definied(var, instr):
    global global_frame
    global local_frame
    global temporary_frame

    frame_error = False

    if 'local_frame' not in globals() and var[:3] == "LF@":
        frame_error = True
    elif 'temporary_frame' not in globals() and var[:3] == "TF@":
        frame_error = True
    elif 'global_frame' not in globals() and var[:3] == "GF@":
        frame_error = True

    # Frame not found
    if frame_error:
        sys.stderr.write("ERROR : SEMANTIC : On line %s Trying to reach an undefinied frame in instr: %s\n" %(instr.get_instr_pos(), instr.get_instr_name()))
        exit(55)

    # search the global frame
    if var[:3] == "GF@":
        for name in global_frame:
            if name.get_name() == var:
                return name

    # search the local frame
    if var[:3] == "LF@":
        if 'local_frame' in globals():
            try:
                act_lf = local_frame[-1]
            except IndexError:
                sys.stderr.write("ERROR : SEMANTIC : On line %s Trying to reach an undefinied frame in instr: %s\n" %(instr.get_instr_pos(), instr.get_instr_name()))
                exit(55)

            for name in local_frame:
                if name.get_name() == var:
                    return name

    # Search in temporary_frame
    if var[:3] == "TF@":
        if 'temporary_frame' in globals():
            for name in temporary_frame:
                if name.get_name() == var:
                    return name

    sys.stderr.write("ERROR : SEMANTIC : Undefinied variable: %s in instruction: %s\n" %(var, instr.get_instr_name()))
    exit(54)

## Handles semantic check of instr move
#
# @param instr instruction given to analysis
def handle_move(instr):
    global global_frame

    # first argument <var> checking for its existance in global frame
    a_var = instr.get_specific_arg(1)   # <var>
    a_symb = instr.get_specific_arg(2)  # <symb>
    var1 = var_is_definied(a_var.get('var'), instr)    # var object

    # <var> <var> situation
    if a_symb.get('var') is not None:
        var2 = var_is_definied(a_symb.get('var'), instr)

        # move value from var2 to var1
        var1.set_value(var2.get_value(), var2.get_type())
    else:
        # value of <symb> into var1
        var1.set_value(next(iter(a_symb.values())), list(a_symb.keys())[0])

## Handles defvar oprations
#
# @param instr given instr
def handle_defvar(instr):
    global global_frame
    global local_frame
    global temporary_frame

    a_var = instr.get_specific_arg(1)
    redefinition = False

    # Check variable frame
    if a_var.get('var')[:3] == 'GF@':
        # Loop over global frame to check for redefinition
        for gf_var in global_frame:
            if gf_var.get_name() == a_var.get('var'):
                redefinition = True

        # If variable is not definied yet - define
        new_var = Variable(a_var.get('var'))
        global_frame.append(new_var)

    if a_var.get('var')[:3] == 'LF@':
        if 'local_frame' in globals():
            try:
                act_lf = local_frame[-1]
            except IndexError:
                sys.stderr.write("ERROR : SEMANTIC : On line %s Trying to reach an undefinied frame in instr: %s\n" %(instr.get_instr_pos(), instr.get_instr_name()))
                exit(55)
            for name in local_frame:
                if name.get_name() == a_var.get('var'):
                    redefinition = True
        else:
            sys.stderr.write("ERROR : SEMANTIC : On line %s Trying to reach an undefinied frame in instr: %s\n" %(instr.get_instr_pos(), instr.get_instr_name()))
            exit(55)
        new_var = Variable(a_var.get('var'))
        # Append to active local frame
        act_lf.append(new_var)
        # Insert active back
        local_frame[-1] = act_lf

    elif a_var.get('var')[:3] == 'TF@':
        if 'temporary_frame' in globals():
            for name in temporary_frame:
                if name.get_name() == a_var.get('var'):
                    redefinition = True
        else:
            sys.stderr.write("ERROR : SEMANTIC : On line %s Trying to reach an undefinied frame in instr: %s\n" %(instr.get_instr_pos(), instr.get_instr_name()))
            exit(55)
        new_var = Variable(a_var.get('var'))
        temporary_frame.append(new_var)

    if redefinition:
        sys.stderr.write("ERROR : SEMANTIC : Trying to redefine existing variable %s\n" %a_var.get('var'))
        exit(52)

## Creating new temporary frame and removing present
#
# @param instr given createframe instr
def handle_createframe(instr):

    # Check if temporary frame already exists
    if 'temporary_frame' not in globals():
        global temporary_frame
        temporary_frame = []
    # delete existing temporary frame items
    else:
        temporary_frame.clear()
        temporary_frame = []

## Pushing existing temporary_frame to stack and can be accessed as local_frame
#
# @param instr given instruction
def handle_pushframe(instr):

    # local frame does not exits yet
    if 'local_frame' not in globals():
        global local_frame
        local_frame = []    # init LF as stack
    else:
        if 'temporary_frame' not in globals():
            sys.stderr.write("ERROR : SEMANTIC : On line %s Trying to reach an undefinied frame in instr: %s\n" %(instr.get_instr_pos(), instr.get_instr_name()))
            exit(55)
        global temporary_frame
        if not temporary_frame:
            exit(55)
        local_frame.append(temporary_frame)
        del temporary_frame # deleting TF

## Moves active local frame to temporary frame
#
# @param instr given instr
def handle_popframe(instr):
    global temporary_frame
    global local_frame

    # local frame doesn't exists or it's empty
    if 'local_frame' not in globals() or not local_frame:
        sys.stderr.write("ERROR : SEMANTIC : On line %s Trying to move local frame, but frame is not definied in instruction: %s\n" %(instr.get_instr_pos(), instr.get_instr_name()))
        exit(55)
    # move local frame to temporary frame
    else:
        temporary_frame = local_frame


### Function call instructions ###

## Instruction supports jump on given label and increments program instr reader
#
# @param instr given instr
# @param act_pos actual position of program reader store to stack
def handle_call(instr, act_pos):
    global labels
    global call_stack

    label = instr.get_specific_arg(1)  # <label>
    label_name = next(iter(label.values()))
    exists = False

    if 'labels' in globals():
        for name, pos in labels:
            if name == label_name:
                exists = True
                break
    else:
        exists = False

    if exists:
        # Save incremented actual position
        call_stack.append(int(act_pos) + 1)
        # Jump on label
        return pos
    else:
        sys.stderr.write("ERROR : SEMANTIC : Trying to jump on non-existing label: %s in on line: %s\n" %(label_name, instr.get_instr_pos()))
        exit(52)

def handle_return(instr):
    global call_stack

    if not call_stack:
        sys.stderr.write("ERROR : SEMANTIC : Can not return, call stack is empty\n")
        exit(56)
    # Take out position from call stack and jump on it
    return call_stack.pop()

# Stack instruction saving given instr value to stack
#
# @param instr given instruction
def handle_pushs(instr):
    global data_stack

    symb_val = instr.get_specific_arg(1)    # extract instruct argument

    if symb_val.get('var') is not None: # Check if var is definied before push
        name = var_is_definied(symb_val.get('var'), instr)
        if name.get_value() is None:
            sys.stderr.write("ERROR : SEMANTIC : Trying to work with undefinied value in instruction %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
            exit(56)
        data_stack.append(name)    # put value on stack
    else:
        data_stack.append(symb_val)    # put value on stack

# Stack instruction retrieving given instr value to stack
#
# @param instr given instruction
def handle_pops(instr):
    global data_stack

    a_var = instr.get_specific_arg(1)   # <var>
    var1 = var_is_definied(a_var.get('var'), instr)    # var object

    # stack is empty
    if not data_stack:
        sys.stderr.write("ERROR : SEMANTIC : Stack is empty cannot execute %s\n" %instr.get_instr_name())
        exit(56)
    else:
        stack_val = data_stack.pop()
        # Variable popped from stack
        if isinstance(stack_val, Variable):
            var1.set_value(stack_val.get_value(), stack_val.get_type())
        else:
            var1.set_value(stack_val[next(iter(stack_val))], next(iter(stack_val)))

### Arithmetic instructions ###

## Checks if given <var> has desired type
#
# @param isntr given instruction
# @param curr_var currently examined variable
# @param operands_t desired type
def is_type(instr, curr_var, operands_t):
    if not hasattr(curr_var, 'type'):
        sys.stderr.write("ERROR : SEMANTIC : Trying to work with undefinied value in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit(56)
    if curr_var.get_type() == operands_t:
        return True
    else:
        sys.stderr.write("ERROR : SEMANTIC : Unexpected argument type in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit(53)

## Retrieves value from given symbols and check if they have same type
#
# @param instr given instruction
# @param a_symb1 <symb1>
# @param a_symb2 <symb2>
# @param operands_t desired type of operands
def check_base_arith(instr, a_symb1, a_symb2, operands_t):

    raise_err = False

    # Second operand is variable
    if a_symb1.get('var') is not None:
        var2 = var_is_definied(a_symb1.get('var'), instr)
        if is_type(instr, var2, operands_t):
            var2_val = var2.get_value()

        # Third operand is variable
        if a_symb2.get('var') is not None:
            var3 = var_is_definied(a_symb2.get('var'), instr)
            if is_type(instr, var3, operands_t):
                var3_val = var3.get_value()

        # Third operand is <symb> is typeof: @operands_t
        elif a_symb2.get(operands_t) is not None:
            var3_val = next(iter(a_symb2.values()))
        else:
            raise_err = True

    # Second operand is <symb> is typeof: @operands_t
    elif a_symb1.get(operands_t) is not None:
        var2_val = next(iter(a_symb1.values()))

        # Third operand is variable
        if a_symb2.get('var') is not None:
            var3 = var_is_definied(a_symb2.get('var'), instr)
            if is_type(instr, var3, operands_t):
                var3_val = var3.get_value()

        # Third operand is <symb> is typeof: @operands_t
        elif a_symb2.get(operands_t) is not None:
            var3_val = next(iter(a_symb2.values()))
        else:
            raise_err = True
    else:
        raise_err = True

    if raise_err:
        sys.stderr.write("ERROR : SEMANTIC : Unexpected argument type in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit(53)

    return(var2_val, var3_val)

## Handles add instruction
#
# @param instr given instruction
def handle_add(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied


    # Get value of operands
    operands = check_base_arith(instr, a_symb1, a_symb2, 'int')

    # Operands have same type and sum can be applicated
    v_sum =  int(operands[0]) + int(operands[1])
    var1.set_value(v_sum, 'int')

## Handles sub instruction
#
# @param instr given instruction
def handle_sub(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    operands = check_base_arith(instr, a_symb1, a_symb2, 'int')

    v_sum = int(operands[0]) - int(operands[1])
    var1.set_value(v_sum, 'int')

## Handles mul instruction
#
# @param instr given instruction
def handle_mul(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    operands = check_base_arith(instr, a_symb1, a_symb2, 'int')

    v_sum = int(operands[0]) * int(operands[1])
    var1.set_value(v_sum, 'int')

## Handles idiv instruction
#
# @param instr given instruction
def handle_idiv(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    operands = check_base_arith(instr, a_symb1, a_symb2, 'int')

    if operands[0] == '0' or operands[1] == '0':
        sys.stderr.write("ERROR : SEMANTIC : Zero division on line %s in instruction: %s\n" %(instr.get_instr_pos(), instr.get_instr_name()))
        exit(57)

    v_sum = int(operands[0]) // int(operands[1])
    var1.set_value(v_sum, 'int')

### Relation operads ###

## Searches for type of given symbol and returns it
#
# @param symb symbol which is being examined
# @param instr given instruction
# @return symbol type
def operation_type(symb, instr):
    global global_frame
    global local_frame

    if symb.get('var') is not None:
        var_v = var_is_definied(symb.get('var'), instr)
        if not hasattr(var_v, 'type'):
            sys.stderr.write("ERROR : SEMANTIC : Trying to work with undefinied value in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
            exit(56)
        return var_v.get_type()

    elif symb.get('int') is not None:
        return 'int'

    elif symb.get('string') is not None:
        return 'string'

    elif symb.get('bool') is not None:
        return 'bool'

    elif symb.get('nil') is not None:
        return 'nil'

    else:
        sys.stderr.write("ERROR : SEMANTIC : Unsupported operand type %s in instruction: %s on line %s\n" %(symb, instr.get_instr_name(), instr.get_instr_pos()))
        exit(53)

## Handles lt instruction
#
# @param instr given instruction
def handle_lt(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    # determine type of <symb1> second symbol type must be the same
    operand_type = operation_type(a_symb1, instr)

    operands = check_base_arith(instr, a_symb1, a_symb2, operand_type)

    if operand_type == 'int' or operand_type == 'string':
        if operands[0] < operands[1]:
            var1.set_value('true', 'bool')
        else:
            var1.set_value('false', 'bool')

    elif operand_type == 'bool':
        if operands[0] == 'false' and operands[1] == 'true':  # false has smaller value than true
            var1.set_value('true', 'bool')
        else:
            var1.set_value('false', 'bool')
    elif operand_type == 'nil':
        sys.stderr.write("ERROR : SEMANTIC : Unsupported operand type nil in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit(53)

## Handles gt instruction
#
# @param instr given instruction
def handle_gt(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    # determine type of <symb1> second symbol type must be the same
    operand_type = operation_type(a_symb1, instr)

    operands = check_base_arith(instr, a_symb1, a_symb2, operand_type)

    if operand_type == 'int' or operand_type == 'string':
        if operands[0] > operands[1]:
            var1.set_value('true', 'bool')
        else:
            var1.set_value('false', 'bool')

    elif operand_type == 'bool':
        if operands[0] == 'true' and operands[1] == 'false':  # false has smaller value than true
            var1.set_value('true', 'bool')
        else:
            var1.set_value('false', 'bool')
    elif operand_type == 'nil':
        sys.stderr.write("ERROR : SEMANTIC : Unsupported operand type: nil in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit(53)

## Handles eq instruction
#
# @param instr given instruction
def handle_eq(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    # determine type of <symb1> second symbol type must be the same
    # exception: if one operand is nil comparision with other type is permitted
    operand_type = operation_type(a_symb1, instr)
    operand_type2 = operation_type(a_symb2, instr)

    if operand_type == 'nil' or operand_type2 == 'nil':
        symb1_val = check_single_symb(instr, a_symb1, operand_type)
        symb2_val = check_single_symb(instr, a_symb2, operand_type2)
        operands = (symb1_val, symb2_val)
    else:
        operands = check_base_arith(instr, a_symb1, a_symb2, operand_type)

    # Handle only nil comparision
    if operand_type == 'nil' or operand_type2 == 'nil':
        if operand_type == 'nil' and operand_type2 == 'nil':
            var1.set_value('true', 'bool')
            # Nil compared to any other type results in false
        else:
            var1.set_value('false', 'bool')
    # Comparing other types
    else:
        if operands[0] == operands[1]:
            var1.set_value('true', 'bool')
        else:
            var1.set_value('false', 'bool')

## Handles and instruction
#
# @param instr given instruction
def handle_and(isntr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    operands = check_base_arith(instr, a_symb1, a_symb2, 'bool')

    if operands[0] == 'true' and operands[1] == 'true':
        var1.set_value('true', 'bool')
    else:
        var1.set_value('false', 'bool')

## Handles or instruction
#
# @param instr given instruction
def handle_or(isntr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    operands = check_base_arith(instr, a_symb1, a_symb2, 'bool')

    if operands[0] == 'true' or operands[1] == 'true':
        var1.set_value('true', 'bool')
    else:
        var1.set_value('false', 'bool')

## Checks if given symbol has desired type
#
# @param instr given instruction
# @param symb examined symbol
# @param symb_type desired type
# @param returns value of given symbol
def check_single_symb(instr, symb, symb_type):

    raise_err = False

    # Second operand is variable
    if symb.get('var') is not None:
        var2 = var_is_definied(symb.get('var'), instr)
        if is_type(instr, var2, symb_type):
            var2_val = var2.get_value()

        else:
            raise_err = True
    # Second operand is <symb> {@symb_type}
    elif symb.get(symb_type) is not None:
        var2_val = next(iter(symb.values()))

    else:
        raise_err = True

    if raise_err:
        sys.stderr.write("ERROR : SEMANTIC : Unexpected argument type in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit(53)

    return var2_val

## Handles not instruction
#
# @param instr given instruction
def handle_not(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    var2_val = check_single_symb(instr, a_symb1, 'bool')

    # Negation of value
    if var2_val == 'true':
        var2_val = 'false'
    else:
        var2_val = 'true'

    var1.set_value(var2_val, 'bool')

## Handles int2char instruction
#
# @param instr given instruction
def handle_int2_char(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    operand_type = operation_type(a_symb1, instr)

    if operand_type == 'var' or operand_type == 'int':

        var2_val = check_single_symb(instr, a_symb1, 'int') # ---------------------possible string@9 ???????

        if 0 <= int(var2_val) <= 1114111:
            chr_val = chr(int(var2_val))
            var1.set_value(chr_val, 'string')
        else:
            sys.stderr.write("ERROR : SEMANTIC : Instruction: %s operand value: %s out of bounds\n" %(instr.get_instr_name(), var2_val))
            exit(58)
    else:
        sys.stderr.write("ERROR : SEMANTIC : Unexpected argument type in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit(53)

## Handles stri2int instruction
#
# @param instr given instruction
def handle_stri2_int(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    operand_type1 = operation_type(a_symb1, instr)
    operand_type2 = operation_type(a_symb2, instr)

    var2_val = check_single_symb(instr, a_symb1, operand_type1)
    var3_val = check_single_symb(instr, a_symb2, operand_type2)

    if operand_type1 == 'string' or operand_type1 == 'var' and operand_type2 == 'var' or operand_type2 == 'int':
        if len(str(var2_val)) <= int(var3_val) or int(var3_val) < 0:   # ------------ Write into documentation (-1 not supported)
            sys.stderr.write("ERROR : SEMANTIC : Instruction: %s index: %s is out of bounds\n" %(instr.get_instr_name(), var3_val))
            exit(58)
        else:
            res = ord(var2_val[int(var3_val)])
            var1.set_value(res, 'int')
    else:
        sys.stderr.write("ERROR : SEMANTIC : Unexpected argument type in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit(53)

### Input-output instructions ###

## Handles read instruction
#
# @param instr given instruction
# @param input_from defines if read read from stdin or file
def handle_read(instr, input_from):

    a_var = instr.get_specific_arg(1)   # <var>
    symb = instr.get_specific_arg(2)  # <symb>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied
    symb_val = next(iter(symb.values()))

    check_input = input_from.get_attrib()

    if check_input[1] is not None:
        try:
            if not os.access(check_input[1], os.R_OK):
                sys.stderr.write("ERROR : FILE : could not read from file - weak permissions\n")
                exit(11)
            source_file = open(check_input[1], "r")

        except FileNotFoundError:
            sys.stderr.write("ERROR : FILE : given file does not exists\n")
            exit(11)
        res = source_file.readline()
        source_file.close()

    # load input from stdin
    else:
        res = input()

    if symb_val == 'int':
        if res is not None:
            # try for valid integer
            try:
                res = int(res)
            except ValueError as e:
                res = int(0)
        else:
            res = int(0)

    elif symb_val == 'bool':
        if res.lower() == 'true':
            res = 'true'
        else:
            res = 'false'
    elif symb_val == 'string' and res is None:
        res = ''

    var1.set_value(res, symb_val)

## Handles write instruction
#
# Prints value of given symbol to stdout
# @param instr given instruction
def handle_write(instr):

    symb = instr.get_specific_arg(1)  # <symb>
    operand_type = operation_type(symb, instr)

    symb_val = check_single_symb(instr, symb, operand_type)

    if operand_type == 'bool':
        if symb_val == 'true':
            print ('true', end='')
        elif symb_val == 'false':
            print ('false', end='')
    # Print nothing on nil chain
    elif operand_type == 'nil':
        print('', end='')
    else:
        print(symb_val, end='')

### Instructions for chains ###

## Handles concat instruction
#
# @param instr given instruction
def handle_concat(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    operand_type1 = operation_type(a_symb1, instr)
    operand_type2 = operation_type(a_symb2, instr)

    if operand_type1 == 'var' or operand_type1 == 'string' and operand_type2 == 'var' or operand_type2 == 'string':
        operands = check_base_arith(instr, a_symb1, a_symb2, operand_type1)

        res = operands[0] + operands[1]
        var1.set_value(res, 'string')
    else:
        sys.stderr.write("ERROR : SEMANTIC : Unexpected argument type in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit(53)


## Handles strlen instruction
#
# @param instr given instruction
def handle_strlen(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied
    operand_type = operation_type(a_symb1, instr)

    if operand_type == 'var' or operand_type == 'string':

        symb_val = check_single_symb(instr, a_symb1, 'string')  #----------------support int, etc?

        res = len(symb_val)
        var1.set_value(res, 'int')
    else:
        sys.stderr.write("ERROR : SEMANTIC : Unexpected argument type in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit(53)


## Handles getchar instruction
#
# @param instr given instruction
def handle_getchar(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    operand_type1 = operation_type(a_symb1, instr)
    operand_type2 = operation_type(a_symb2, instr)
    if operand_type1 == 'var' or operand_type1 == 'string' and operand_type2 == 'var' or operand_type2 == 'int':

        var2_val = check_single_symb(instr, a_symb1, 'string')
        var3_val = int(check_single_symb(instr, a_symb2, 'int'))

        if len(str(var2_val)) <= var3_val or var3_val < 0:   # ------------ Write into documentation (-1 not supported)
            sys.stderr.write("ERROR : SEMANTIC : Instruction: %s index: %s is out of bounds\n" %(instr.get_instr_name(), var3_val))
            exit(58)
        else:
            res = var2_val[var3_val]
            var1.set_value(res, 'string')
    else:
        sys.stderr.write("ERROR : SEMANTIC : Unexpected argument type in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit(53)


## Handles setchar instruction
#
# @param instr given instruction
def handle_set_char(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    operand_type1 = operation_type(a_symb1, instr)
    operand_type2 = operation_type(a_symb2, instr)
    if operand_type1 == 'var' or operand_type1 == 'int' and operand_type2 == 'var' or operand_type2 == 'string':

        var2_val = check_single_symb(instr, a_symb1, operand_type1)
        var3_val = check_single_symb(instr, a_symb2, operand_type2)

        try:
            var2_val = int(var2_val)
        except ValueError:
            sys.stderr.write("ERROR : SEMANTIC : Unexpected argument type in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
            exit(53)
        res = var1.get_value()
        if var2_val < 0 or len(res) <= var2_val:
            sys.stderr.write("ERROR : SEMANTIC : Instruction: %s index: %s is out of bounds\n" %(instr.get_instr_name(), var3_val))
            exit(58)
        else:
            # <symb2> contains more than 1 character
            if len(var3_val) > 1:
                var3_val = var3_val[0]
            elif len(var3_val) == 0:
                sys.stderr.write("ERROR : SEMANTIC : Instruction: %s cannot apply on empty string\n" %(instr.get_instr_name()))
                exit(58)

            # convert to list
            res = list(res)
            # change character on given index
            res[int(var2_val)] = var3_val
            # change back to string
            res = "".join(res)

            var1.set_value(res, 'string')
    else:
        sys.stderr.write("ERROR : SEMANTIC : Unexpected argument type in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit(53)

### Work with types ###

## Handles type instruction
#
# @param instr given instruction
def handle_type(instr):
    global global_frame
    global local_frame

    a_var = instr.get_specific_arg(1)   # <var>
    symb = instr.get_specific_arg(2)  # <symb>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    if symb.get('var') is not None:
        a_var = var_is_definied(symb.get('var'), instr)
        if not hasattr(a_var, 'type'):
            res = ''
        else:
            res = a_var.get_type()

    elif symb.get('int') is not None:
        res = 'int'

    elif symb.get('string') is not None:
        res = 'string'

    elif symb.get('bool') is not None:
        res = 'bool'

    elif symb.get('nil') is not None:
        res = 'nil'

    var1.set_value(res, 'string')

### Flow control instructions ###

## Handles jump instruction
#
# @param instr given instruction
def handle_jump(instr):
    global labels

    label = instr.get_specific_arg(1)  # <label>
    label_name = next(iter(label.values()))

    if 'labels' in globals():
        for name, pos in labels:
            if name == label_name:
                return int(pos)

        sys.stderr.write("ERROR : SEMANTIC : Trying to jump on non-existing label: %s in on line: %s\n" %(label_name, instr.get_instr_pos()))
        exit(52)
    else:
        sys.stderr.write("ERROR : SEMANTIC : Trying to jump on non-existing label: %s in on line: %s\n" %(label_name, instr.get_instr_pos()))
        exit(52)

## Handles jumpifeq instruction
#
# @param instr given instruction
def handle_jumpifeq(instr, act_pos):

    label = instr.get_specific_arg(1)  # <label>
    label_name = next(iter(label.values()))

    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    # Indicates if label exists
    exists = False

    if 'labels' not in globals():
        sys.stderr.write("ERROR : SEMANTIC : Trying to jump on non-existing label: %s in on line: %s\n" %(label_name, instr.get_instr_pos()))
        exit(52)

    for name, pos in labels:
        if name == label_name:
            exists = True
            break

    if not exists:
        sys.stderr.write("ERROR : SEMANTIC : Trying to jump on non-existing label: %s in on line: %s\n" %(label_name, instr.get_instr_pos()))
        exit(52)
    else:

        operand1_type = operation_type(a_symb1, instr)
        operand2_type = operation_type(a_symb2, instr)

        if operand1_type != operand2_type:
            sys.stderr.write("ERROR : SEMANTIC : Operands type do not match in instruction: %s on line: %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
            exit(53)

        symb1_val = check_single_symb(instr, a_symb1, operand1_type)
        symb2_val = check_single_symb(instr, a_symb2, operand1_type)

        # Compare values - can be done by EQ instruction
        if symb1_val == symb2_val:
            return int(pos)
        else:
            return int(act_pos)


## Handles jumpifneq instruction
#
# @param instr given instruction
def handle_jumpifneq(instr, act_pos):

    label = instr.get_specific_arg(1)  # <label>
    label_name = next(iter(label.values()))

    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    # Indicates if label exists
    exists = False

    if 'labels' not in globals():
        sys.stderr.write("ERROR : SEMANTIC : Trying to jump on non-existing label: %s in on line: %s\n" %(label_name, instr.get_instr_pos()))
        exit(52)

    for name, pos in labels:
        if name == label_name:
            exists = True
            break

    if not exists:
        sys.stderr.write("ERROR : SEMANTIC : Trying to jump on non-existing label: %s in on line: %s\n" %(label_name, instr.get_instr_pos()))
        exit(52)
    else:

        operand1_type = operation_type(a_symb1, instr)
        operand2_type = operation_type(a_symb2, instr)

        if operand1_type != operand2_type:
            sys.stderr.write("ERROR : SEMANTIC : Operands type do not match in instruction: %s on line: %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
            exit(53)

        symb1_val = check_single_symb(instr, a_symb1, operand1_type)
        symb2_val = check_single_symb(instr, a_symb2, operand1_type)

        # Compare values - can be done by EQ instruction
        if symb1_val != symb2_val:
            return int(pos)
        else:
            return int(act_pos)

## Handles exit instruction
#
# @param instr given instruction
def handle_exit(instr):

    symb = instr.get_specific_arg(1)  # <symb>
    operand_type = operation_type(symb, instr)

    if operand_type == 'var' or operand_type == 'int':
        symb_val = int(check_single_symb(instr, symb, operand_type))

        if 0 <= symb_val <= 49:
            exit(symb_val)
        else:
            sys.stderr.write("ERROR : SEMANTIC : Invalid value: %s in function %s on line: %s\n" %(symb_val, instr.get_instr_name(), instr.get_instr_pos()))
        exit(57)
    else:
        sys.stderr.write("ERROR : SEMANTIC : Unexpected argument type in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit(53)

### Debug instructions ###

## Handles dprint instruction
#
# @param instr given instruction
def handle_dprint(instr):

    symb = instr.get_specific_arg(1)  # <symb>
    operand_type = operation_type(symb, instr)

    symb_val = check_single_symb(instr, symb, operand_type)

    sys.stderr.write("%s" %symb_val)    # new line or not ? ------------------------------------------


## Handles break instruction
#
# @param instr given instruction
def handle_break(instr):

    global global_frame
    global local_frame

    sys.stderr.write("Currently at instruction %s on line %s\n\n" %(instr.get_instr_name(), instr.get_instr_pos()))
    sys.stderr.write("Instructions parsed: %d\n\n" %(int(instr.get_instr_pos()) - 1))

    sys.stderr.write("Global frame consists of:\n\n")
    for item in global_frame:
        sys.stderr.write("Variable name: %s value: %s\n" %(item.get_name(), item.get_value()))

    sys.stderr.write("\nLocal frame consists of: \n\n")
    if 'local_frame' in globals():
        for item in local_frame:
            sys.stderr.write("Variable name: %s value: %s\n" %(item.get_name(), item.get_value()))
    else:
        sys.stderr.write("Local frame is empty\n")

    sys.stderr.write("\nTemporary frame consists of: \n\n")
    if 'temporary_frame' in globals():
        for item in temporary_frame:
            sys.stderr.write("Variable name: %s value: %s\n" %(item.get_name(), item.get_value()))
    else:
        sys.stderr.write("Temporary frame is empty\n")

################################################################################

# Argument parse
arg_parse = Args(None, None)

if len(sys.argv) == 1:
    sys.stderr.write("ERROR : ARGUMENTS : need argument --source of --input run --help\n")
    exit(10)
elif sys.argv[1] == "--help" and len(sys.argv) < 3: # Help cannot exists with other arguments
    print ('Usage python3 interpret.py --help | [--input=path | --source=path]\n', \
            'Interpret of language .IPPcode19 written in XML format.\n\n',\
            '   --help          prints help message\n',\
            '   --input=path    specifies path to input file for IPPcode19 instructions\n',\
            '   --source=path   specifies path to source code file of IPPcode19\n\n',\
            'Interpret checks given XML input and control lexical, syntax and semantic of\n',\
            'given code.'
            )
    exit(0);

# more arguments then supported
if len(sys.argv) > 3:
    sys.stderr.write("ERROR : ARGUMENTS : too many arguments run --help for further info\n")
    exit(10)

# search for --input and --source
if len(sys.argv) == 3:
    if re.search('^(--source=)+', sys.argv[1]) and re.search('^(--input=)+', sys.argv[2]):
        arg_parse.set_source((sys.argv[1])[9:])
        arg_parse.set_input((sys.argv[2])[8:])
    elif re.search('^(--input=)+', sys.argv[1]) and re.search('^(--source=)+', sys.argv[2]):
        arg_parse.set_input((sys.argv[1])[8:])
        arg_parse.set_source((sys.argv[2])[9:])
    else:
        sys.stderr.write("ERROR : ARGUMENTS : unknown arguments run --help for further info\n")
elif len(sys.argv) == 2:
    if re.search('^(--source=)+', sys.argv[1]):
        arg_parse.set_source((sys.argv[1])[9:])
    elif re.search('^(--input=)+', sys.argv[1]):
        arg_parse.set_input((sys.argv[1])[8:])
    else:
        sys.stderr.write("ERROR : ARGUMENTS : unknown arguments run --help for further info\n")
        exit(10)

if((arg_parse.get_attrib())[0] is not None):
    source_file_name = (arg_parse.get_attrib())[0]

    # Checks for rights for read from file
    try:
        if not os.access(source_file_name, os.R_OK):
            sys.stderr.write("ERROR : FILE : could not read from file - weak permissions\n")
            exit(11)
        source_file = open(source_file_name, "r")

    except FileNotFoundError:
        sys.stderr.write("ERROR : FILE : given file does not exists\n")
        exit(11)


    source_xml = ""
    for line in source_file:
        source_xml = source_xml + line

    try:
        tree = elem_tree.parse(source_file_name) # Creating ElementTree object
    except elem_tree.ParseError:
        sys.stderr.write("ERROR : XML : XML file is not well-formed\n")
        exit(31)

    root = parse_xml(tree) # Retrieve root
    source_file.close()

else:
    source_xml = ""
    for line in sys.stdin:
        source_xml = source_xml + line

# Try to get root - any error results in not well-formed xml
try:
    root = elem_tree.fromstring(source_xml)

except elem_tree.ParseError:
    sys.stderr.write("ERROR : XML : XML file is not well-formed\n")
    exit(31)

# List of out instructions
instruct_list = list()

# parse given XML and create obj for every instruction
for instr in root.iter('instruction'):
    act = Instruction(instr)
    instruct_list.append(act)   # insert all instructions into list

    # Store all labels
    if(act.get_instr_name() == 'LABEL'):
        label = act.get_specific_arg(1)
        label_name = next(iter(label.values()))

        for name, pos in labels:
            if name == label_name:
                sys.stderr.write("ERROR : SEMANTIC : Trying to redefine existing label: %s in on line: %s\n" %(label_name, act.get_instr_pos()))
                exit(52)
        # Store label name and position as tuple
        labels.append(( label_name, act.get_instr_pos() ))

# Sorting list by order attribute
instruct_list.sort(key=lambda x: int(x.line), reverse=False)

# Duplicate order attribute
i = 0
while(i < len(instruct_list)):
    if i > 0:
        if instruct_list[i-1].get_instr_pos() == instruct_list[i].get_instr_pos():
             sys.stderr.write("ERROR : XML : file is not well formed duplicate order attribute in instrucion: %s\n" %(instruct_list[i].get_instr_name()))
             exit(32)
    i += 1

act_pos = 0

# loop over instruction list
while int(act_pos) < len(instruct_list):
    instr = instruct_list[act_pos]
    act_pos += 1
    args = instr.get_arg_val()
    # loop over tuple of instruction's arguments
    for arg_n in args:
        # loop over dictionary == arg values and LEXICAL ANALYSIS
        for i_type, i_val in arg_n.items():

            if i_type == 'var':
                parse_var(i_val)
            elif i_type == 'int':
                parse_int(i_val)
            elif i_type == 'string':
                p_string = parse_string(i_val)
                instr.update_val(arg_n, p_string)

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
                exit(32)

    # SYNTAX ANALYSIS
    syntax_check(instr)

    # Work with frames
    if (instr.get_instr_name()).upper() == 'MOVE':
        handle_move(instr)
    elif (instr.get_instr_name()).upper() == 'CREATEFRAME':
        handle_createframe(instr)
    elif (instr.get_instr_name()).upper() == 'PUSHFRAME':
        handle_pushframe(instr)
    elif (instr.get_instr_name()).upper() == 'POPFRAME':
        handle_popframe(instr)
    elif (instr.get_instr_name()).upper() == 'DEFVAR':
        handle_defvar(instr)

    # Function call instructions
    elif (instr.get_instr_name()).upper() == 'CALL':
        act_pos = int(handle_call(instr, act_pos))
    elif (instr.get_instr_name()).upper() == 'RETURN':
        act_pos = handle_return(instr)

    # Stack instructions
    elif (instr.get_instr_name()).upper() == 'PUSHS':
        handle_pushs(instr)
    elif (instr.get_instr_name()).upper() == 'POPS':
        handle_pops(instr)

    # Arithmetic instructions
    elif (instr.get_instr_name()).upper() == 'ADD':
        handle_add(instr)
    elif (instr.get_instr_name()).upper() == 'SUB':
        handle_sub(instr)
    elif (instr.get_instr_name()).upper() == 'MUL':
        handle_mul(instr)
    elif (instr.get_instr_name()).upper() == 'IDIV':
        handle_idiv(instr)

    # Relation instructions
    elif (instr.get_instr_name()).upper() == 'LT':
        handle_lt(instr)
    elif (instr.get_instr_name()).upper() == 'GT':
        handle_gt(instr)
    elif (instr.get_instr_name()).upper() == 'EQ':
        handle_eq(instr)

    # Logic instructions
    elif (instr.get_instr_name()).upper() == 'AND':
        handle_and(instr)
    elif (instr.get_instr_name()).upper() == 'OR':
        handle_or(instr)
    elif (instr.get_instr_name()).upper() == 'NOT':
        handle_not(instr)

    # Convert instructions
    elif (instr.get_instr_name()).upper() == 'INT2CHAR':
        handle_int2_char(instr)
    elif (instr.get_instr_name()).upper() == 'STRI2INT':
        handle_stri2_int(instr)

    # Input-output instructions
    elif (instr.get_instr_name()).upper() == 'READ':
        handle_read(instr, arg_parse)
    elif (instr.get_instr_name()).upper() == 'WRITE':
        handle_write(instr)

    # Work with chains
    elif (instr.get_instr_name()).upper() == 'CONCAT':
        handle_concat(instr)
    elif (instr.get_instr_name()).upper() == 'STRLEN':
        handle_strlen(instr)
    elif (instr.get_instr_name()).upper() == 'GETCHAR':
        handle_getchar(instr)
    elif (instr.get_instr_name()).upper() == 'SETCHAR':
        handle_set_char(instr)

    # Work with types
    elif (instr.get_instr_name()).upper() == 'TYPE':
        handle_type(instr)

    # Flow control instructions
    elif (instr.get_instr_name()).upper() == 'LABEL':
        # Label instruction is handled above in previous semantic check for labels in source
        pass
    elif (instr.get_instr_name()).upper() == 'EXIT':
        handle_exit(instr)
    elif (instr.get_instr_name()).upper() == 'JUMP':
        # Jump can change the flow of processing instructions by jumping on label
        act_pos = int(handle_jump(instr))
    elif (instr.get_instr_name()).upper() == 'JUMPIFEQ':
        act_pos = int(handle_jumpifeq(instr, act_pos))
    elif (instr.get_instr_name()).upper() == 'JUMPIFNEQ':
        act_pos = int(handle_jumpifneq(instr, act_pos))

    # Debug instructions
    elif (instr.get_instr_name()).upper() == 'DPRINT':
            handle_dprint(instr)
    elif (instr.get_instr_name()).upper() == 'BREAK':
            handle_break(instr)

## End of file            