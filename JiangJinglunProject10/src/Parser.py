keyword = {
    'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
    'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'}
operator = {"+", "-", "*", "/", "|", "&lt;", "&gt;", '&amp;', "="}
unary_operator = {"-", "~"}
symbol = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}
xml_symbol = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}

class Parser:
    def __init__(self, code_lines):
        self.output = "" # Empty string to store the result
        self.code_lines = code_lines
        self.indent_level = 0
        self.current_index = 1
    
    # The entry point for the parser
    def parse(self):
        self.parse_class()

    def tag_start(self, tag):
        self.output += '    ' * self.indent_level + tag + '\n'
        self.indent_level += 1

    def tag_end(self, tag):
        self.indent_level -= 1
        self.output += '    ' * self.indent_level + tag + '\n'

    def compile_next(self):
        self.output += '    ' * self.indent_level + self.code_lines[self.current_index]
        self.current_index += 1

    def is_op(self):
        tag, attribute = self.extract(self.code_lines[self.current_index])
        return attribute in operator

    def is_unary_op(self):
        tag, attribute = self.extract(self.code_lines[self.current_index])
        return attribute in unary_operator

    def dec(self):
        self.compile_next()  # var
        self.compile_next()  # keyword/identifier
        self.compile_next()  # varName
        # Handle the case when there are several variables of the same type
        while ',' in self.code_lines[self.current_index]:
            self.compile_next()  # ,
            self.compile_next()  # varName
        self.compile_next()  # ;

    def compile_class_var(self):
        self.tag_start("<classVarDec>")
        self.dec()
        self.tag_end("</classVarDec>")

    def compile_term(self):
        self.tag_start("<term>")
        if self.is_unary_op():
            self.compile_next()  # unaryOp
            self.compile_term()
        elif '(' in self.code_lines[self.current_index]:
            self.compile_next()  # (
            self.compile_expression()
            self.compile_next()  # )
        else:
            self.compile_next()  # id
            if '[' in self.code_lines[self.current_index]:
                self.compile_next()  # [ 
                self.compile_expression()
                self.compile_next()  # ]
            # Handles the case when is an object method
            elif '.' in self.code_lines[self.current_index]:
                self.compile_next()  # .
                self.compile_next()  # id
                self.compile_next()  # (
                self.compile_expression_lst()
                self.compile_next()  # )
            # Handles the function call
            elif '(' in self.code_lines[self.current_index]:
                self.compile_next()  # .
                self.compile_expression_lst()
                self.compile_next()  # )
        self.tag_end("</term>")

    def compile_expression(self):
        self.tag_start("<expression>")
        self.compile_term()
        while self.is_op():
            self.compile_next()  # Op
            self.compile_term()
        self.tag_end("</expression>")

    def compile_expression_lst(self):
        self.tag_start("<expressionList>")
        if ')' not in self.code_lines[self.current_index]:
            self.compile_expression()
        while ')' not in self.code_lines[self.current_index]:
            self.compile_next()  # <symbol> , </symbol>
            self.compile_expression()
        self.tag_end("</expressionList>")

    def compile_function(self):
        self.tag_start("<subroutineDec>")
        self.compile_next()  # constructor/method/function
        self.compile_next()  # return type: void/type
        self.compile_next()  # function name
        self.compile_next()  # (
        
        self.tag_start("<parameterList>")
        if ')' not in self.code_lines[self.current_index]:
            self.compile_next()  # type/className
            self.compile_next()  # varName

        # Handle the case when multiple parameters exist
        while ')' not in self.code_lines[self.current_index]:
            self.compile_next()  # ,
            self.compile_next()  # type/className
            self.compile_next()  # varName
        self.tag_end("</parameterList>")
        self.compile_next()  # )

        self.tag_start("<subroutineBody>")
        self.compile_next()  # {
        while "var" in self.code_lines[self.current_index]:
          self.tag_start("<varDec>")
          self.dec()
          self.tag_end("</varDec>")
        self.compile_statements()
        self.compile_next()  # }
        self.tag_end("</subroutineBody>")

        self.tag_end("</subroutineDec>")

    def compile_statements(self):
        self.tag_start("<statements>")
        while 1:
            if 'let' in self.code_lines[self.current_index]:
                self.compile_let_statement()
            elif 'if' in self.code_lines[self.current_index]:
                self.compile_if_statement()
            elif 'while' in self.code_lines[self.current_index]:
                self.compile_while_statement()
            elif 'do' in self.code_lines[self.current_index]:
                self.compile_do_statement()
            elif 'return' in self.code_lines[self.current_index]:
                self.compile_return_statement()
            else:
                break
        self.tag_end("</statements>")
    
    def compile_let_statement(self):
        self.tag_start("<letStatement>")
        self.compile_next()  # let
        self.compile_next()  # id
        # Handle the case when the next part of the statement involves array indexing
        if '[' in self.code_lines[self.current_index]:
            self.compile_next()  # [
            self.compile_expression()
            self.compile_next()  # ]
        self.compile_next()  # = 
        self.compile_expression()
        self.compile_next()  # ;
        self.tag_end("</letStatement>")

    def compile_if_statement(self):
        self.tag_start("<ifStatement>")
        self.compile_next()  # <keyword> if </keyword>
        self.compile_next()  # <symbol> ( </symbol>
        self.compile_expression()
        self.compile_next()  # <symbol> ) </symbol>

        self.compile_next()  # <symbol> { </symbol>
        self.compile_statements()
        self.compile_next()  # <symbol> } </symbol>

        if "else" in self.code_lines[self.index]:
            self.compile_next()  # <keyword> else </keyword>
            self.compile_next()  # <symbol> { </symbol>
            self.compile_statements()
            self.compile_next()  # <symbol> } </symbol>

        self.tag_end("</ifStatement>")

    def compile_while_statement(self):
        # while_code = "<whileStatement>"
        self.tag_start("<whileStatement>")
        self.compile_next()  # <keyword> while </keyword>
        self.compile_next()  # <symbol> ( </symbol>
        self.compile_expression()
        self.compile_next()  # <symbol> ) </symbol>
        self.compile_next()  # <symbol> { </symbol>
        self.compile_statements()
        self.compile_next()  # <symbol> } </symbol>

        self.tag_end("</whileStatement>")

    def compile_do_statement(self):
        self.tag_start("<doStatement>")
        self.compile_next()  # <keyword> do </keyword>

        # subroutine call can create a sparate method
        self.compile_next()  # <identifier> subroutineName </identifier>
        if '.' in self.code_lines[self.current_index]:
            self.compile_next()  # <symbol> . </symbol>
            self.compile_next()  # <symbol> subroutineName </symbol>
        self.compile_next()  # <symbol> ( </symbol>
        self.compile_expression_lst()
        self.compile_next()  # <symbol> ) </symbol>
        self.compile_next()  # <symbol> ; </symbol>

        self.tag_end("</doStatement>")

    def compile_return_statement(self):
        self.tag_start("<returnStatement>")
        self.compile_next()  # <keyword> return </keyword>
        if ';' not in self.code_lines[self.current_index]:
            self.compile_expression()
        self.compile_next()  # <symbol> ; </symbol>
        self.tag_end("</returnStatement>")

    def parse_class(self):
        self.tag_start("<class>")
        self.compile_next()  # class
        self.compile_next()  # className
        self.compile_next()  # { 
        # Compile the variables
        while (('static' in self.code_lines[self.current_index]) or ('field' in self.code_lines[self.current_index])):
            self.compile_class_var()
        # Compile the functions in the class
        while 'constructor' in self.code_lines[self.current_index] or 'function' in self.code_lines[self.current_index] or 'method' in \
                self.code_lines[self.current_index]:
            self.compile_function()
        self.compile_next()  # } 
        self.tag_end("</class>")

    def extract(self, xml_code: str):
        for index, c in enumerate(xml_code):
            if c == ">":
                tag = xml_code[1:index]
                attribute_index = index + 2
            elif c == "<" and index > 0:
                attribute = xml_code[attribute_index:index - 1]
                return tag, attribute