import re

pattern = re.compile("(\{|\}|\(|\)|\[|\]|\.|\,|\;|\+|\-|\*|\/|\&|\||\<|\>|\=|\~| )")
keyword = {
    'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
    'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'}
operator = {"+", "-", "*", "/", "|", "&lt;", "&gt;", '&amp;', "="}
unary_operator = {"-", "~"}
symbol = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}
xml_symbol = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}

def tokens(codes):
    code = "<tokens>\n"
    xml_code = ["<tokens>\n"]

    for line in codes:
        output, xml_output = tokenizer(line)
        code += output
        xml_code += xml_output

    code += "</tokens>"
    xml_code += ["</tokens>"]
    return code, xml_code

def tokenizer(code_line):
    output = ""
    xml_output = []
    code_words = re.split(re.compile(pattern), code_line)
    string_tag = False
    for word in code_words:
        if len(word) != 0:
            if string_tag == True:
                if word[-1] == '"':
                    string_tag = False
                    if len(word) != 1:
                        string_constant += word[:-1]
                    output += "<stringConstant> " + string_constant + " </stringConstant>\n"
                    xml_output.append("<stringConstant> " + string_constant + " </stringConstant>\n")
                else:
                    string_constant += word
            elif word[0] == '"':
                if word[-1] == '"':
                    string_constant = word[1:-1]
                else:
                    string_tag = True
                    string_constant = word[1:]

            elif word != ' ':
                if word in keyword:
                    output += "<keyword> " + word + " </keyword>\n"
                    xml_output.append("<keyword> " + word + " </keyword>\n")
                elif word in symbol:
                    if word in xml_symbol:
                        output += "<symbol> " + xml_symbol[word] + " </symbol>\n"
                        xml_output.append("<symbol> " + xml_symbol[word] + " </symbol>\n")
                    else:
                        output += "<symbol> " + word + " </symbol>\n"
                        xml_output.append("<symbol> " + word + " </symbol>\n")
                elif word.isdigit():
                    output += "<integerConstant> " + word + " </integerConstant>\n"
                    xml_output.append("<integerConstant> " + word + " </integerConstant>\n")
                else:
                    output += "<identifier> " + word + " </identifier>\n"
                    xml_output.append("<identifier> " + word + " </identifier>\n")

    return output, xml_output


class Parser:
    def __init__(self, code_lines):
        self.output = ""
        self.code_lines = code_lines
        self.indent_level = 0
        self.current_index = 0

    def parse(self):
        # Entry method to start parsing
        while self.current_index < len(self.code_lines):
            self.parse_next_token()

    def parse_next_token(self):
        # Central method to dispatch parsing based on the current token
        token, token_type = self.get_current_token()
        if token_type == "keyword":
            self.parse_keyword(token)
        elif token_type == "symbol":
            self.parse_symbol(token)
        # Add more conditions as necessary for other token types

    def get_current_token(self):
        # Simplified token extraction method
        token = self.code_lines[self.current_index]
        token_type = self.identify_token_type(token)
        self.current_index += 1
        return token, token_type

    def identify_token_type(self, token):
        # Dummy method, replace logic with actual token type identification
        if token in keyword:
            return "keyword"
        elif token in symbol:
            return "symbol"
        # Add more conditions for other types
        return "unknown"

    def parse_keyword(self, keyword):
        # Example of handling different keywords
        if keyword == "class":
            self.start_tag("class")
            self.parse_class()
            self.end_tag("class")
        # Handle other keywords similarly

    def parse_class(self):
        # Parse the class structure
        self.expect("identifier")  # Class name
        self.expect("{")  # Opening brace
        while not self.check("}"):
            self.parse_class_content()
        self.expect("}")  # Closing brace

    def parse_class_content(self):
        # Example of parsing content within a class
        next_token, _ = self.get_current_token()
        if next_token in ["static", "field"]:
            self.parse_class_var_dec()
        elif next_token in ["constructor", "function", "method"]:
            self.parse_subroutine()

    def expect(self, expected_type):
        # Ensure the next token matches the expected type and advance
        token, token_type = self.get_current_token()
        if token_type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token_type}")
        # Optionally, process the token

    def check(self, expected_token):
        # Check if the next token matches the expected without advancing
        token, _ = self.get_current_token()
        return token == expected_token

    def start_tag(self, tag):
        self.output += ' ' * self.indent_level + f"<{tag}>\n"
        self.indent_level += 4

    def end_tag(self, tag):
        self.indent_level -= 4
        self.output += ' ' * self.indent_level + f"</{tag}>\n"

    def parse_class_var_dec(self):
        # Parses class variable declarations (static or field)
        self.start_tag("classVarDec")
        # Assuming next tokens are type and varName
        self.expect("type")  # This is a placeholder; implement proper type checking
        self.expect("identifier")
        while self.check(","):
            self.expect(",")
            self.expect("identifier")
        self.expect(";")
        self.end_tag("classVarDec")

    def parse_subroutine(self):
        # Parses a subroutine declaration (constructor, function, method)
        self.start_tag("subroutineDec")
        # Assuming next tokens are return type, subroutine name, and parameters
        self.expect("returnType")  # This is a placeholder; implement proper return type checking
        self.expect("identifier")
        self.parse_parameter_list()
        self.parse_subroutine_body()
        self.end_tag("subroutineDec")

    def parse_parameter_list(self):
        # Parses the parameter list of a subroutine
        self.start_tag("parameterList")
        if not self.check(")"):
            self.expect("type")  # This is a placeholder; implement proper type checking
            self.expect("identifier")
            while self.check(","):
                self.expect(",")
                self.expect("type")  # Again, placeholder
                self.expect("identifier")
        self.end_tag("parameterList")

    def parse_subroutine_body(self):
        # Parses the body of a subroutine
        self.start_tag("subroutineBody")
        self.expect("{")
        while self.check("var"):
            self.parse_var_dec()
        self.parse_statements()
        self.expect("}")
        self.end_tag("subroutineBody")

    def parse_var_dec(self):
        # Parses a variable declaration
        self.start_tag("varDec")
        self.expect("var")
        self.expect("type")  # Placeholder
        self.expect("identifier")
        while self.check(","):
            self.expect(",")
            self.expect("identifier")
        self.expect(";")
        self.end_tag("varDec")

    def parse_statements(self):
        # Parses a series of statements
        self.start_tag("statements")
        # A loop to handle multiple types of statements
        while not self.check("}"):  # Assuming end of statements is marked by a closing curly brace
            next_token, _ = self.get_current_token()
            if next_token == "let":
                self.parse_let_statement()
            elif next_token == "if":
                self.parse_if_statement()
            # Add handling for other statement types (while, do, return)
        self.end_tag("statements")
