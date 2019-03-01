import xml.etree.ElementTree as elem_tree
from io import StringIO
import sys
import re
import os

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

arg_parse = Args("None", "None")

if len(sys.argv) == 1:
    sys.stderr.write("ERROR : ARGUMENTS : need argument --source of --input run --help\n");
    exit()
elif sys.argv[1] == "--help" and len(sys.argv) < 3:
    print("Help message");
    exit(0);

if len(sys.argv) > 3:
    sys.stderr.write("ERROR : ARGUMENTS : too many arguments run --help for further info\n");
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
        sys.stderr.write("ERROR : ARGUMENTS : unknown arguments run --help for further info\n");
elif len(sys.argv) == 2:
    if re.search('^(--source=)+', sys.argv[1]):
        print("source")
        arg_parse.set_source((sys.argv[1])[9:])
    elif re.search('^(--input=)+', sys.argv[1]):
        print("input")
        arg_parse.set_input((sys.argv[1])[8:])
    else:
        sys.stderr.write("ERROR : ARGUMENTS : unknown arguments run --help for further info\n");
        exit()

if((arg_parse.get_attrib())[0] != "None"):
    source_file = (arg_parse.get_attrib())[0]
    try:
        if not os.access(source_file, os.R_OK):
            sys.stderr.write("ERROR : FILE : could not read from file - weak permissions\n");
            exit()
        source_file = open(source_file, "r")

    except FileNotFoundError:
        sys.stderr.write("ERROR : FILE : given file does not exists\n");
        exit()
    except elem_tree.ParseError:
        sys.stderr.write("ERROR : XML : XML file is not well-formed\n");
        exit()

else:
    source_xml = ""
    for line in sys.stdin:
        source_xml = source_xml + line


try:
    xml_file = elem_tree.fromstring(source_xml)

except elem_tree.ParseError:
    sys.stderr.write("ERROR : XML : XML file is not well-formed\n");
    exit()
