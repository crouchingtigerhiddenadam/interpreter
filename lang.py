"""
## License
The MIT License (MIT)
Copyright (C)2020 CrouchingTigerHiddenAdam @tigerhiddenadam
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

datatype = None
objects = {}
pos = 0
result = None
code = """

    procedure precedent;
    begin
        x := 1 + 2 * 3 + 4;
        writeln x
    end;

    procedure recursive;
    begin
        i := i + 1;
        writeln i;
        if i < 10 then
        begin
            call recursive
        end
    end;

    procedure main;
    begin
        i := 0;

        call precedent;
        call recursive;

        i := 100;
        while i < 110 do
        begin
            i := i + 1;
            writeln i
        end
    end;

    call main

"""


class Object:
    def __init__(self, datatype, ident, value):
        self.datatype = datatype
        self.ident = ident
        self.value = value


def program():
    global code
    global pos

    while pos < len(code):

        if not procedure_definition() and not statement():
            raise error("Syntax Error: statement expected")

        if pos < len(code) and not code[pos] == ";":
            break

        pos = pos + 1

    trivia()
    if pos < len(code):
        raise error("Syntax Error: unexpended end of file")


def procedure_definition():
    global code
    global objects
    global pos

    if not keyword("procedure"):
        return False

    if not identifier():
        raise error("Syntax Error: ident expected")

    ident = result 

    if code[pos] != ';':
        raise error("Syntax Error: semicolon expected")

    pos = pos + 1
    objects[ident] = Object("procedure", ident, pos)

    if not begin_statement(True):
        raise error("Syntax Error: begin statement expected")

    return True


def statement(scanonly = False):
    global code
    global pos

    if begin_statement(scanonly):
        return True

    if call_statement(scanonly):
        return True

    if if_statement(scanonly):
        return True

    if while_statement(scanonly):
        return True

    if writeln_statement(scanonly):
        return True

    # note: assign statements must always be last
    if assign_statement(scanonly):
        return True

    return False


def call_statement(scanonly = False):
    global code
    global objects
    global pos

    if not keyword("call"):
        return False

    if not identifier():
        raise error("Syntax Error: ident expected")

    ident = result

    if ident not in objects:
        raise error("Syntax Error: procedure does not exist")

    if not scanonly:
        obj = objects[ident]
        return_pos = pos

        if obj.datatype != "procedure":
            raise error("Syntax Error: procedure expected")

        pos = obj.value
        statement(scanonly)
        pos = return_pos

    return True


def if_statement(scanonly = False):
    global code
    global pos

    if not keyword("if"):
        return False

    condition(scanonly)

    if not keyword("then"):
        raise error("Syntax Error: then expected")

    if not statement(scanonly or not result):
        raise error("Syntax Error: statement expected")

    return True


def writeln_statement(scanonly = False):
    global code
    global pos

    if not keyword("writeln"):
        return False

    expression(scanonly)

    if not scanonly:
        if datatype == "integer":
            print(str(result))
        else:
            raise error("Type Mismatch: integer expected")

    return True


def while_statement(scanonly = False):
    global code
    global pos

    if not keyword("while"):
        return False

    continue_pos = pos

    condition(scanonly)
    semaphore = scanonly or not result

    if not keyword("do"):
        raise error("System Error: do expected")

    if not statement(semaphore):
        raise error("System Error: statement expected")

    while not semaphore:
        pos = continue_pos
        condition(False)
        semaphore = not result

        keyword("do")
        statement(semaphore)

    return True


def begin_statement(scanonly = False):
    global code
    global pos

    if not keyword("begin"):
        return False

    if statement(scanonly):
        while pos < len(code) and code[pos] == ";":
            pos = pos + 1
            if not statement(scanonly):
                raise error("Syntax Error: statement expected")

    if not keyword("end"):
        raise error("Syntax Error: end keyword expected")

    return True


def assign_statement(scanonly = False):
    global code
    global objects
    global pos

    if not identifier(scanonly):
        return False

    ident = result

    if pos < len(code) and code[pos] == ":":
        pos = pos + 1
        if pos < len(code) and code[pos] == "=":
            pos = pos + 1

            expression(scanonly)

            if not scanonly:
                objects[ident] = Object(datatype, ident, result)

            return True

    return False


def keyword(word):
    global code
    global pos

    trivia()
    start = pos

    for letter in word:
        if pos < len(code) and code[pos] != letter:
            pos = start
            return False 
        pos = pos + 1

    if pos < len(code) and not trivia() and code[pos] != ";":
        pos = start
        return False

    return True


def condition(scanonly = False):
    global code
    global datatype
    global pos
    global result

    term(scanonly)

    ldatatype = datatype
    lvalue = result

    # equality
    if pos < len(code) and code[pos] == "=":
        pos = pos + 1

        expression(scanonly)

        if not scanonly:
            if ldatatype == "integer" and datatype == "integer":
                datatype = "boolean"
                lvalue = lvalue == result
            else:
                raise error("Type Mismatch: integer expected")

    # less-than
    elif pos < len(code) and code[pos] == "<":
        pos = pos + 1

        expression(scanonly)

        if not scanonly:
            if ldatatype == "integer" and datatype == "integer":
                datatype = "boolean"
                lvalue = lvalue < result
            else:
                raise error("Type Mismatch: integer expected")

    # greater-than
    elif pos < len(code) and code[pos] == ">":
        pos = pos + 1

        expression(scanonly)

        if not scanonly:
            if ldatatype == "integer" and datatype == "integer":
                datatype = "boolean"
                lvalue = lvalue > result
            else:
                raise error("Type Mismatch: integer expected")

    result = lvalue


def expression(scanonly = False):
    global code
    global datatype
    global pos
    global result

    term(scanonly)

    ldatatype = datatype
    lvalue = result

    while pos < len(code):

        # plus
        if code[pos] == "+":
            pos = pos + 1

            term(scanonly)

            if not scanonly:
                if ldatatype == "integer" and datatype == "integer":
                    lvalue = lvalue + result
                else:
                    raise error("Type Mismatch: integer expected")

        # minus
        elif code[pos] == "-":
            pos = pos + 1

            term(scanonly)

            if not scanonly:
                if ldatatype == "integer" and datatype == "integer":
                    lvalue = lvalue + result
                else:
                    raise error("Type Mismatch: integer expected")

        # passthrough
        else:
            break

    result = lvalue

def term(scanonly = False):
    global code
    global datatype
    global pos
    global result

    factor(scanonly)

    ldatatype = datatype
    lvalue = result

    while pos < len(code):

        # multiply
        if code[pos] == "*":
            pos = pos + 1

            factor(scanonly)

            if not scanonly:
                if ldatatype == "integer" and datatype == "integer":
                    lvalue = lvalue * result
                else:
                    raise error("Type Mismatch: integer expected")

        # division
        elif code[pos] == "/":
            pos = pos + 1

            factor(scanonly)

            if not scanonly:
                if ldatatype == "integer" and datatype == "integer":
                    if value == 0:
                        raise error("Zero Division: divide by zero")
                    lvalue = lvalue / result
                else:
                    raise error("Type Mismatch: integer expected")

        # passthrough
        else:
            break

    result = lvalue

def factor(scanonly = False):
    global code
    global datatype
    global pos
    global objects
    global result

    trivia()
    start = pos

    # integer literal
    if pos < len(code) and (
        code[pos] >= "0" and code[pos] <= "9"):
        pos = pos + 1

        while pos < len(code) and (
            code[pos] >= "0" and code[pos] <= "9"):
            pos = pos + 1

        datatype = "integer"
        result = int(code[start:pos])

        trivia()

    # variable
    elif identifier(scanonly):

        if not scanonly:
            ident = result

            if ident not in objects:
                raise error("Syntax Error: variable expected")

            obj = objects[ident]
            datatype = obj.datatype
            result = obj.value

    else:
        raise error("Syntax Error: factor expected")


def identifier(scanonly = False):
    global code
    global datatype
    global pos
    global result

    trivia()
    start = pos

    if pos < len(code) and (
        code[pos] >= "A" and code[pos] <= "Z" or
        code[pos] >= "a" and code[pos] <= "z"):
        pos = pos + 1
        while pos < len(code) and (
            code[pos] >= "A" and code[pos] <= "Z" or
            code[pos] >= "a" and code[pos] <= "z"):
            pos = pos + 1

        if not scanonly:
            datatype = "identifier"
            result = code[start:pos]

        # reserved word check
        if result in [
            "begin",
            "do",
            "end",
            "if",
            "procedure",
            "then",
            "writeln",
            "while"]:
            raise error("Syntax Error: reserved word used")

        trivia()
        return True

    else:
        return False


def trivia():
    global code
    global pos

    if pos < len(code) and code[pos] in " \n\r\t":
        pos = pos + 1
        while pos < len(code) and code[pos] in " \n\r\t":
            pos = pos + 1
        return True

    return False


def error(message):
    global code
    global pos

    error_pos = pos
    line_num = 0
    pos = 0

    while pos < len(code) and pos < error_pos:

        # linux and unix newlines
        if code[pos] == '\n':
            line_num = line_num + 1
            pos = pos + 1

        # mac and windows newlines
        elif code[pos] == '\r':
            line_num = line_num + 1
            pos = pos + 1
            if code[pos] == '\n':
                pos = pos + 1

        else:
            pos = pos + 1

    return Exception("{} on line {}".format(message, line_num))


program()
