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

from enum import Enum
from typing import Dict


class DataType(Enum):
    BOOLEAN = 0,
    FUNCTION = 1,
    INTEGER = 2,
    SYMBOL = 3


class Interpreter:


    def __init__(self, code: str):
        self.code = code
        self.datatype: DataType = None
        self.objects: Dict[str, Object] = {}
        self.position: int = 0
        self.result: any = None


    def run(self):
        self.program()


    def program(self):

        while self.position < len(self.code):

            if not self.procedure_definition() and not self.statement():
                raise error("Syntax Error: statement expected")

            if self.position < len(self.code) and not self.code[self.position] == ";":
                break

            self.position = self.position + 1

        self.trivia()
        if self.position < len(self.code):
            raise self.error("Syntax Error: unexpended end of file")


    def procedure_definition(self) -> bool:

        if not self.keyword("procedure"):
            return False

        if not self.identifier():
            raise self.error("Syntax Error: ident expected")

        ident = self.result 

        if self.code[self.position] != ';':
            raise self.error("Syntax Error: semicolon expected")

        self.position = self.position + 1
        self.objects[ident] = Object("procedure", ident, self.position)

        if not self.begin_statement(True):
            raise self.error("Syntax Error: begin statement expected")

        return True


    def statement(self, scanonly: bool = False) -> bool:

        if self.begin_statement(scanonly):
            return True

        if self.call_statement(scanonly):
            return True

        if self.if_statement(scanonly):
            return True

        if self.while_statement(scanonly):
            return True

        if self.writeln_statement(scanonly):
            return True

        # note: assign statements must always be last
        if self.assign_statement(scanonly):
            return True

        return False


    def call_statement(self, scanonly: bool = False) -> bool:

        if not self.keyword("call"):
            return False

        if not self.identifier():
            raise self.error("Syntax Error: ident expected")

        ident = self.result

        if ident not in self.objects:
            raise self.error("Syntax Error: procedure does not exist")

        if not scanonly:
            obj = self.objects[ident]
            return_position = self.position

            if obj.datatype != "procedure":
                raise self.error("Syntax Error: procedure expected")

            self.position = obj.value
            self.statement(scanonly)
            self.position = return_position

        return True


    def if_statement(self, scanonly: bool = False) -> bool:

        if not self.keyword("if"):
            return False

        self.condition(scanonly)

        if not self.keyword("then"):
            raise self.error("Syntax Error: then expected")

        if not self.statement(scanonly or not self.result):
            raise self.error("Syntax Error: statement expected")

        return True


    def writeln_statement(self, scanonly: bool = False) -> bool:

        if not self.keyword("writeln"):
            return False

        self.expression(scanonly)

        if not scanonly:
            if self.datatype == DataType.INTEGER:
                print(str(self.result))
            else:
                raise self.error("Type Mismatch: integer expected")

        return True


    def while_statement(self, scanonly: bool = False) -> bool:

        if not self.keyword("while"):
            return False

        continue_position = self.position

        self.condition(scanonly)
        semaphore = scanonly or not self.result

        if not self.keyword("do"):
            raise self.error("System Error: do expected")

        if not self.statement(semaphore):
            raise self.error("System Error: statement expected")

        while not semaphore:
            self.position = continue_position
            self.condition()
            semaphore = not self.result

            self.keyword("do")
            self.statement(semaphore)

        return True


    def begin_statement(self, scanonly: bool = False) -> bool:

        if not self.keyword("begin"):
            return False
        
        if self.statement(scanonly):
            while self.position < len(self.code) and self.code[self.position] == ";":
                self.position = self.position + 1
                if not self.statement(scanonly):
                    raise self.error("Syntax Error: statement expected")

        if not self.keyword("end"):
            raise self.error("Syntax Error: end keyword expected")

        return True


    def assign_statement(self, scanonly: bool = False) -> bool:

        if not self.identifier(scanonly):
            return False

        ident = self.result

        if self.position < len(self.code) and self.code[self.position] == ":":
            self.position = self.position + 1
            if self.position < len(self.code) and self.code[self.position] == "=":
                self.position = self.position + 1

                self.expression(scanonly)

                if not scanonly:
                    self.objects[ident] = Object(self.datatype, ident, self.result)

                return True

        return False


    def keyword(self, word: str) -> bool:

        self.trivia()
        start = self.position

        for letter in word:
            if self.position < len(self.code) and self.code[self.position] != letter:
                self.position = start
                return False 
            self.position = self.position + 1

        if self.position < len(self.code) and not self.trivia() and self.code[self.position] != ";":
            self.position = start
            return False

        return True


    def condition(self, scanonly: bool = False) -> bool:

        self.term(scanonly)

        ldatatype = self.datatype
        lvalue = self.result

        # equality
        if self.position < len(self.code) and self.code[self.position] == "=":
            self.position = self.position + 1

            self.expression(scanonly)

            if not scanonly:
                if ldatatype == DataType.INTEGER and self.datatype == DataType.INTEGER:
                    self.datatype = DataType.BOOLEAN
                    lvalue = lvalue == self.result
                else:
                    raise self.error("Type Mismatch: integer expected")

        # less-than
        elif self.position < len(self.code) and self.code[self.position] == "<":
            self.position = self.position + 1

            self.expression(scanonly)

            if not scanonly:
                if ldatatype == DataType.INTEGER and self.datatype == DataType.INTEGER:
                    self.datatype = DataType.BOOLEAN
                    lvalue = lvalue < self.result
                else:
                    raise self.error("Type Mismatch: integer expected")

        # greater-than
        elif self.position < len(self.code) and self.code[self.position] == ">":
            self.position = self.position + 1

            self.expression(scanonly)

            if not scanonly:
                if ldatatype == DataType.INTEGER and self.datatype == DataType.INTEGER:
                    self.datatype = DataType.BOOLEAN
                    lvalue = lvalue > self.result
                else:
                    raise self.error("Type Mismatch: integer expected")

        self.result = lvalue


    def expression(self, scanonly: bool = False):

        self.term(scanonly)

        ldatatype = self.datatype
        lvalue = self.result

        while self.position < len(self.code):

            # plus
            if self.code[self.position] == "+":
                self.position = self.position + 1

                self.term(scanonly)

                if not scanonly:
                    if ldatatype == DataType.INTEGER and self.datatype == DataType.INTEGER:
                        lvalue = lvalue + self.result
                    else:
                        raise self.error("Type Mismatch: integer expected")

            # minus
            elif self.code[self.position] == "-":
                self.position = self.position + 1

                self.term(scanonly)

                if not scanonly:
                    if ldatatype == DataType.INTEGER and self.datatype == DataType.INTEGER:
                        lvalue = lvalue + self.result
                    else:
                        raise self.error("Type Mismatch: integer expected")

            # passthrough
            else:
                break

        self.result = lvalue


    def term(self, scanonly = False):
        self.factor(scanonly)

        ldatatype = self.datatype
        lvalue = self.result

        while self.position < len(self.code):

            # multiply
            if self.code[self.position] == "*":
                self.position = self.position + 1

                self.factor(scanonly)

                if not scanonly:
                    if ldatatype == DataType.INTEGER and self.datatype == DataType.INTEGER:
                        lvalue = lvalue * self.result
                    else:
                        raise self.error("Type Mismatch: integer expected")

            # division
            elif self.code[self.position] == "/":
                self.position = self.position + 1

                self.factor(scanonly)

                if not scanonly:
                    if ldatatype == DataType.INTEGER and self.datatype == DataType.INTEGER:
                        if self.result == 0:
                            raise self.error("Zero Division: divide by zero")
                        lvalue = lvalue / self.result
                    else:
                        raise self.error("Type Mismatch: integer expected")

            # passthrough
            else:
                break

        self.result = lvalue


    def factor(self, scanonly: bool = False):

        self.trivia()
        start = self.position

        # integer literal
        if self.position < len(self.code) and (
            self.code[self.position] >= "0" and self.code[self.position] <= "9"):
            self.position = self.position + 1

            while self.position < len(self.code) and (
                self.code[self.position] >= "0" and self.code[self.position] <= "9"):
                self.position = self.position + 1

            if not scanonly:
                self.datatype = DataType.INTEGER
                self.result = int(self.code[start:self.position])

            self.trivia()

        # variable
        elif self.identifier(scanonly):

            if not scanonly:
                ident = self.result

                if ident not in self.objects:
                    raise self.error("Syntax Error: variable expected")

                obj = self.objects[ident]
                self.datatype = obj.datatype
                self.result = obj.value

        else:
            raise self.error("Syntax Error: factor expected")


    def identifier(self, scanonly: bool = False) -> bool:

        self.trivia()
        start = self.position

        if self.position < len(self.code) and (
            self.code[self.position] >= "A" and self.code[self.position] <= "Z" or
            self.code[self.position] >= "a" and self.code[self.position] <= "z"):
            self.position = self.position + 1
            while self.position < len(self.code) and (
                self.code[self.position] >= "A" and self.code[self.position] <= "Z" or
                self.code[self.position] >= "a" and self.code[self.position] <= "z"):
                self.position = self.position + 1

            if not scanonly:
                self.datatype = DataType.SYMBOL
                self.result = self.code[start:self.position]

            # reserved word check
            if self.result in [
                "begin",
                "do",
                "end",
                "if",
                "procedure",
                "then",
                "writeln",
                "while"]:
                raise self.error("Syntax Error: reserved word used")

            self.trivia()
            return True

        else:
            return False


    def trivia(self) -> bool:
        if self.position < len(self.code) and self.code[self.position] in " \n\r\t":
            self.position = self.position + 1
            while self.position < len(self.code) and self.code[self.position] in " \n\r\t":
                self.position = self.position + 1
            return True

        return False


    def error(self, message: str) -> Exception:
        error_position = self.position
        line_num = 0
        self.position = 0

        while self.position < len(self.code) and self.position < error_position:

            # linux and unix newlines
            if self.code[self.position] == '\n':
                line_num = line_num + 1
                self.position = self.position + 1

            # mac and windows newlines
            elif self.code[self.position] == '\r':
                line_num = line_num + 1
                self.position = self.position + 1
                if self.code[self.position] == '\n':
                    self.position = self.position + 1

            else:
                self.position = self.position + 1

        return Exception(f"{message} on line {line_num}")


class Object:
    def __init__(self, datatype: str, ident: str, value: any):
        self.datatype = datatype
        self.ident = ident
        self.value = value


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


interpreter = Interpreter(code)
interpreter.run()
