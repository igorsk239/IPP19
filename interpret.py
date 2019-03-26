import xml.etree.ElementTree as elem_tree
from io import StringIO
import sys
import re
import os

#dict print only
import pprint


# TODO read from stdin not only from file
# TODO stack pop determine type of popped value -> set variable type
# TODO sort instructions by order HACK
# TODO sort arguments by order  HACK

# TODO jump return number or number--   <- must be --

# GF global frame structured as dictionary
global_frame = []
# Data stack used by stack instructions
data_stack = []
# Stack used for storage of position of intern counter
call_stack = []
# List of labels present in source code
labels = []

# local_frame
# temporary_frame

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

class Variable:
    def __init__(self, name):
        self.name = name
        self.value = None

    def set_value(self, value, op_type):
        self.value = value;
        self.type = op_type
    def get_value(self):
        return self.value
    def get_type(self):
        return self.type
    def get_name(self):
        return self.name


class Instruction:
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

    def get_instr_args(self):
        return (self.arg1, self.arg2, self.arg3)

    def get_arg_val(self):
        return (self.arg1Val, self.arg2Val, self.arg3Val)

    def get_arg_total(self):
        t_arg = self.get_arg_val()
        arg_sum = 0
        for arg in t_arg:
            for arg_val in arg:
                if arg_val is not None:
                    arg_sum += 1
        return arg_sum

    def get_specific_arg(self, position):
        if position == 1:
            return self.arg1Val
        elif position == 2:
            return self.arg2Val
        elif position == 3:
            return self.arg3Val
        else:
            raise ValueError('Unknown position number in method get_specific_arg\n')

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

# Functions for XML parsing
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
    # pprint.pprint(op_val[3:])
    if re.search('GF@|LF@|TF@', op_val[:3]) is None:
        sys.stderr.write("ERROR : lexical error in given stream : %s frame expected\n" %op_val[:3])
        exit()
    if re.search('^[a-zA-Z_\-\$&%\*!?][a-zA-Z_\-\$&%\*!?0-9]*$', op_val[3:]) is None:
        sys.stderr.write("ERROR : lexical error in given stream : %s identifier expected\n" %op_val)
        exit()

def parse_label(op_val):
    if re.search('^[a-zA-Z_\-\$&%\*!?][a-zA-Z_\-\$&%\*!?0-9]*$', op_val) is None:
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

################################################################################

# Functions for syntax analysis
def arg_count(instr, exp):

    if instr.get_arg_total() != exp:
        sys.stderr.write("ERROR : SYNTAX Wrong number of arguments in %s expected %d\n" %(instr.get_instr_name(), exp))
        exit()
    else:
        return True

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

def syntax_struct(instr, instr_number):

    instr_args = instr.get_arg_val()  # all arguments of instruction

    if 1 <= instr_number <= 5:
        # if instr_args.count(None) != len(instr_args):
        if instr.get_arg_total() != 0:
            sys.stderr.write("ERROR : SYNTAX Unknown operand in instruction: %s\n" %instr.get_instr_name())
            exit()

    elif 6 <= instr_number <= 8:
        if instr.get_arg_total() != 1 or next(iter(instr_args[0])) != 'label':
            sys.stderr.write("ERROR : SYNTAX Wrong number of arguments or argument type in %s\n" %instr.get_instr_name())
            exit()

    elif 9 <= instr_number <= 10:
        if instr.get_arg_total() != 1 or next(iter(instr_args[0])) != 'var':
            sys.stderr.write("ERROR : SYNTAX Wrong number of arguments or argument type in %s\n" %instr.get_instr_name())
            exit()

    elif 11 <= instr_number <= 14:
        arg_count(instr, 1)
        if not is_symbol(next(iter(instr_args[0]))):
            sys.stderr.write("ERROR : SYNTAX Wrong type of argument in %s\n" %instr.get_instr_name())
            exit()

    elif 15 <= instr_number <= 19:
        arg_count(instr, 2)
        if next(iter(instr_args[0])) != 'var' or not is_symbol(next(iter(instr_args[1]))):
            sys.stderr.write("ERROR : SYNTAX Wrong type of argument in %s\n" %instr.get_instr_name())
            exit()

    elif 20 <= instr_number <= 32:
        arg_count(instr, 3)
        if next(iter(instr_args[0])) != 'var' or not is_symbol(next(iter(instr_args[1]))) or not is_symbol(next(iter(instr_args[2]))):
            sys.stderr.write("ERROR : SYNTAX Wrong type of argument in %s\n" %instr.get_instr_name())
            exit()

    elif 33 <= instr_number <= 34:
        if next(iter(instr_args[0])) != 'label' or not is_symbol(next(iter(instr_args[1]))) or not is_symbol(next(iter(instr_args[2]))):
            sys.stderr.write("ERROR : SYNTAX Wrong type of argument in %s\n" %instr.get_instr_name())
            exit()

    elif instr_number == 35:
        arg_count(instr, 2)
        if instr_args[0].get('var') is None or instr_args[1].get('type') is None:
            sys.stderr.write("ERROR : SYNTAX Wrong type of argument in %s\n" %instr.get_instr_name())
            exit()


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
def var_is_definied(var, instr):
    global global_frame
    global local_frame
    global temporary_frame

    frame_error = False

    # search the global frame
    for name in global_frame:
        if name.get_name() == var:
            return name

    # search the local frame
    if 'local_frame' in globals():
        act_lf = local_frame[-1]
        for name in local_frame:
            if name.get_name() == var:
                return name

    elif 'local_frame' not in globals() and var[:3] == "LF@":
        frame_error = True

    # Search in temporary_frame
    if 'temporary_frame' in globals():
        for name in temporary_frame:
            if name.get_name() == var:
                return name
    elif 'local_frame' not in globals() and var[:3] == "LF@":
        frame_error = True

    # Frame not found
    if frame_error:
        sys.stderr.write("ERROR : SEMANTIC : On line %s Trying to reach an undefinied frame in instr: %s\n" %(instr.get_instr_pos(), instr.get_instr_name()))
        exit(55)

    sys.stderr.write("ERROR : SEMANTIC : Undefinied variable: %s in instruction: %s\n" %(var, instr.get_instr_name()))
    exit()

def handle_move(instr):
    global global_frame

    # first argument <var> checking for its existance in global frame
    a_var = instr.get_specific_arg(1)   # <var>
    a_symb = instr.get_specific_arg(2)  # <symb>
    var1 = var_is_definied(a_var.get('var'), instr)    # var object
    # pprint.pprint(list(a_symb.keys())[0])

    # <var> <var> situation
    if a_symb.get('var') is not None:
        var2 = var_is_definied(a_symb.get('var'), instr)

        # move value from var2 to var1
        var1.set_value(var2.get_value(), var2.get_type())
        # print ("HERE: var1: %s  var2: %s" % (var1.get_value(), var2.get_value()))
    else:
        # value of <symb> into var1
        var1.set_value(next(iter(a_symb.values())), list(a_symb.keys())[0])

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
            act_lf = local_frame[-1]
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
        temporary_frame.append(a_var.get('var'))

    if redefinition:
        sys.stderr.write("ERROR : SEMANTIC : Trying to redefine existing variable %s\n" %a_var.get('var'))
        exit()

def handle_createframe(instr):

    # Check if temporary frame already exists
    if 'temporary_frame' not in globals():
        global temporary_frame
        temporary_frame = []
    # delete existing temporary frame items
    else:
        temporary_frame.clear()
        temporary_frame = []

def handle_pushframe(instr):
    global temporary_frame

    # local frame does not exits yet
    if 'local_frame' not in globals():
        global local_frame
        local_frame = []    # init LF as stack
    else:
        if 'temporary_frame' not in globals():
            sys.stderr.write("ERROR : SEMANTIC : On line %s Trying to reach an undefinied frame in instr: %s\n" %(instr.get_instr_pos(), instr.get_instr_name()))
            exit(55)
        local_frame.append(temporary_frame)
        del temporary_frame # deleting TF

def handle_popframe(instr):
    global temporary_frame
    global local_frame

    # local frame doesn't exists or it's empty
    if 'local_frame' not in globals() or not local_frame:
        sys.stderr.write("ERROR : SEMANTIC : On line %s Trying to move local frame, but frame is not definied in instruction: %s\n" %(instr.get_instr_pos(), instr.get_instr_name()))
        exit(55)
    # move local frame to temporary frame
    else:
        temporary_frame.clear()
        temporary_frame = local_frame


# Function call instructions
def handle_call(instr, act_pos):
    global labels
    global call_stack

    label = instr.get_specific_arg(1)  # <label>
    label_name = next(iter(label.values()))
    exist = False

    for name, pos in labels:
        if name == label_name:
            exists = True
            break

    if not exist:
        sys.stderr.write("ERROR : SEMANTIC : Trying to jump on non-existing label: %s in on line: %s\n" %(label_name, instr.get_instr_pos()))
        exit(52)
    else:
        # Save incremented actual position
        call_stack.append(int(act_pos) + 1)
        # Jump on label
        return pos

def handle_return(instr):
    global call_stack

    # Take out position from call stack and jump on it
    return call_stack.pop() # stack is emty error type ??? -------------------------------------

# Stack instructions
def handle_pushs(instr):
    global data_stack

    symb_val = instr.get_specific_arg(1)    # extract instruct argument
    data_stack.append(next(iter(symb_val.values())))    # put value on stack

def handle_pops(instr):
    global data_stack

    a_var = instr.get_specific_arg(1)   # <var>
    var1 = var_is_definied(a_var.get('var'), instr)    # var object

    # stack is empty
    if not data_stack:
        sys.stderr.write("ERROR : SEMANTIC : Stack is empty cannot execute %s\n" %instr.get_instr_name())
        exit(56)
    else:
        # pprint.pprint(data_stack)
        var1.set_value(data_stack.pop(), None)    # HERE have to set variable type based on output!!
        # pprint.pprint(data_stack)

# Arithmetic instructions
def is_type(instr, curr_var, operands_t):
    if not hasattr(curr_var, 'type'):
        sys.stderr.write("ERROR : SEMANTIC : Trying to work with undefinied value in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit()
    if curr_var.get_type() == operands_t:
        return True
    else:
        sys.stderr.write("ERROR : SEMANTIC : Unexpected argument type in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
        exit()

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
        exit()

    return(var2_val, var3_val)


def handle_add(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    # pprint.pprint(a_symb1)

    # Get value of operands
    operands = check_base_arith(instr, a_symb1, a_symb2, 'int')

    # Operands have same type and sum can be applicated
    v_sum =  int(operands[0]) + int(operands[1])
    var1.set_value(v_sum, 'int')
    # print ("--------------")
    # print (var1.get_value())
    # print (var1.get_type())
    # print (var1.get_name())

def handle_sub(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    operands = check_base_arith(instr, a_symb1, a_symb2, 'int')

    v_sum = int(operands[0]) - int(operands[1])
    var1.set_value(v_sum, 'int')

def handle_mul(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    operands = check_base_arith(instr, a_symb1, a_symb2, 'int')

    v_sum = int(operands[0]) * int(operands[1])
    var1.set_value(v_sum, 'int')

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

# Relation operads
def operation_type(symb, instr):
    global global_frame
    global local_frame

    if symb.get('var') is not None:
        var_v = var_is_definied(symb.get('var'), instr)
        if not hasattr(var_v, 'type'):
            sys.stderr.write("ERROR : SEMANTIC : Trying to work with undefinied value in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
            exit()
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
        exit()

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
        exit()

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
    # Comparing nil values
    # else:
    #     sys.stderr.write("ERROR : SEMANTIC : Unsupported operand type in instruction: %s on line %s\n" %(instr.get_instr_name(), instr.get_instr_pos()))
    #     exit()

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

def check_single_symb(instr, symb, symb_type):

    raise_err = False

    # Second operand is variable
    if symb.get('var') is not None:
        var2 = var_is_definied(symb.get('var'), instr)
        if is_type(instr, var2, symb_type):
            var2_val = var2.get_value()

        else:
            raise_err = True
    # Second operand is <symb> {int}
    elif symb.get(symb_type) is not None:
        var2_val = next(iter(symb.values()))

    else:
        raise_err = True

    if raise_err:
        sys.stderr.write("ERROR : SEMANTIC : Unexpected argument type in instruction: %s on line %s\n" %(instr.get_instr_name, instr.get_instr_pos))
        exit()

    return var2_val

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

def handle_int2_char(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    var2_val = check_single_symb(instr, a_symb1, 'int') # ---------------------possible string@9 ???????

    if 0 <= var2_val <= 1114111:
        chr_val = chr(var2_val)
        var1.set_value(chr_val, 'string')
    else:
        sys.stderr.write("ERROR : SEMANTIC : Instruction: %s operand value: %s out of bounds\n" %(instr.get_instr_name(), var2_val))
        exit(58)

def handle_stri2_int(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    var2_val = check_single_symb(instr, a_symb1, 'string')
    var3_val = check_single_symb(instr, a_symb2, 'int')

    if len(str(var2_val)) < int(var3_val) or int(var3_val) < 0:   # ------------ Write into documentation (-1 not supported)
        sys.stderr.write("ERROR : SEMANTIC : Instruction: %s index: %s is out of bounds\n" %(instr.get_instr_name(), var3_val))
        exit(58)
    else:
        res = ord(var2_val[var3_val])
        var1.set_value(res, 'int')

# Input-output instructions
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
                exit()
            source_file = open(check_input[1], "r")

        except FileNotFoundError:
            sys.stderr.write("ERROR : FILE : given file does not exists\n")
            exit()
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

# Instructions for chains
def handle_concat(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    operands = check_base_arith(instr, a_symb1, a_symb2, 'string')

    res = operands[0] + operands[1]

    var1.set_value(res, 'string')

def handle_strlen(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied
    # operand_type = operation_type(a_symb1, instr)

    symb_val = check_single_symb(instr, a_symb1, 'string')  #----------------support int, etc?

    res = len(symb_val)

    var1.set_value(res, 'int')

def handle_getchar(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    var2_val = check_single_symb(instr, a_symb1, 'string')
    var3_val = check_single_symb(instr, a_symb2, 'int')

    if len(str(var2_val)) < int(var3_val) or int(var3_val) < 0:   # ------------ Write into documentation (-1 not supported)
        sys.stderr.write("ERROR : SEMANTIC : Instruction: %s index: %s is out of bounds\n" %(instr.get_instr_name(), var3_val))
        exit(58)
    else:
        res = var2_val[var3_val]
        var1.set_value(res, 'string')

def handle_set_char(instr):

    a_var = instr.get_specific_arg(1)   # <var>
    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    var1 = var_is_definied(a_var.get('var'), instr)    # <var> is definied

    var2_val = check_single_symb(instr, a_symb1, 'int')
    var3_val = check_single_symb(instr, a_symb2, 'string')

    res = var1.get_value()
    if int(var2_val) < 0 or len(res) < int(var2_val):
        sys.stderr.write("ERROR : SEMANTIC : Instruction: %s index: %s is out of bounds\n" %(instr.get_instr_name(), var3_val))
        exit(58)
    else:
        # <symb2> contains more than 1 character
        if len(var3_val) > 1:
            var3_val = var3_val[1]

        # convert to list
        res = list(res)
        # change character on given index
        res[int(var2_val)] = var3_val
        # change back to string
        res = "".join(res)

        var1.set_value(res, 'string')

    # pprint.pprint(var1.get_value())

# Work with types
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

    # pprint.pprint(var1.get_value())

# def handle_label(instr):
#     # global labels
#     #
#     # label = instr.get_specific_arg(1)  # <label>
#     # label_name = next(iter(label.values()))
#     #
#     # for name, pos in labels:
#     #     if name == label_name:
#     #         sys.stderr.write("ERROR : SEMANTIC : Trying to redefine existing label: %s in on line: %s\n" %(label_name, instr.get_instr_pos()))
#     #         exit(52)
#     #
#     # labels.append((label_name,instr.get_instr_pos()))
#     #
#     # pprint.pprint(labels)
#     pass

# Flow control instructions
def handle_jump(instr):
    global labels

    label = instr.get_specific_arg(1)  # <label>
    label_name = next(iter(label.values()))

    for name, pos in labels:
        if name == label_name:
            return int(pos)

    sys.stderr.write("ERROR : SEMANTIC : Trying to jump on non-existing label: %s in on line: %s\n" %(label_name, instr.get_instr_pos()))
    exit(52)

def handle_jumpifeq(instr, act_pos):

    label = instr.get_specific_arg(1)  # <label>
    label_name = next(iter(label.values()))

    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    # Indicates if label exists
    exists = False

    for name, pos in labels:
        if name == label_name:
            exists = True
            break

    if not exits:
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

def jumpifneq(instr, act_pos):

    label = instr.get_specific_arg(1)  # <label>
    label_name = next(iter(label.values()))

    a_symb1 = instr.get_specific_arg(2)  # <symb1>
    a_symb2 = instr.get_specific_arg(3)  # <symb2>

    # Indicates if label exists
    exists = False

    for name, pos in labels:
        if name == label_name:
            exists = True
            break

    if not exits:
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

def handle_exit(instr):

    symb = instr.get_specific_arg(2)  # <symb>

    symb_val = (instr, symb, 'int')

    if 0 < symb_val < 50:
        exit(symb_val)
    else:
        sys.stderr.write("ERROR : SEMANTIC : Invalid value: %s in function %s on line: %s\n" %(symb_val, instr.get_instr_name(), instr.get_instr_pos()))
        exit(57)

# Debug instructions
def handle_dprint(instr):

    symb = instr.get_specific_arg(1)  # <symb>
    operand_type = operation_type(symb, instr)

    symb_val = check_single_symb(instr, symb, operand_type)

    sys.stderr.write("%s" %symb_val)    # new line or not ? ------------------------------------------

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
    exit()
elif sys.argv[1] == "--help" and len(sys.argv) < 3:
    print("Help message");
    exit(0);

if len(sys.argv) > 3:
    sys.stderr.write("ERROR : ARGUMENTS : too many arguments run --help for further info\n")
    exit()

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
source_file.close()

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
                exit()

    # SYNTAX ANALYSIS
    syntax_check(instr)

    # print (instr.get_instr_name())

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
        handle_call(instr)
    elif (instr.get_instr_name()).upper() == 'RETURN':
        handle_return(instr)

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
        # handle_label(instr)
        # Label instruction is handled above in previous semantic check for labels in source
        pass
    elif (instr.get_instr_name()).upper() == 'EXIT':
        handle_exit(instr)
    elif (instr.get_instr_name()).upper() == 'JUMP':
        # Jump can change the flow of processing instructions by jumping on label
        act_pos = handle_jump(instr)
    elif (instr.get_instr_name()).upper() == 'JUMPIFEQ':
        act_pos = handle_jumpifeq(instr, act_pos)
    elif (instr.get_instr_name()).upper() == 'JUMPIFNEQ':
        act_pos = handle_jumpifneq(instr)

    # Debug instructions
    elif (instr.get_instr_name()).upper() == 'DPRINT':
            handle_dprint(instr)
    elif (instr.get_instr_name()).upper() == 'BREAK':
            handle_break(instr)
