class JackTokenizer():

    def __init__(self, jackfile):
        with open(jackfile, 'r') as self.jackf:
            self.code = self.jackf.read()

        self._token_type = ''
        self._keyword = ''
        self._symbol = ''
        self._identifier = ''
        self._int_val = 0
        self._string_val = ''
        self.i = 0
        self.code_len = len(self.code)

    def has_more_tokens(self):
        return self.i < self.code_len - 1

    def advance(self):

        alpha_num = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789'
        symbol = '()[]\{\},;=.+-*&|~<>'
        keyword = ('class', 'constructor', 'function', 'method', 'field', 'static', 'var', 
            'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do',
            'if', 'else', 'while', 'return',)
        
        tmp = ''

        if self.code[self.i].isspace():
            self._token_type = ''
            while self.has_more_tokens() and self.code[self.i].isspace():
                self.i += 1

        if self.code[self.i] in alpha_num:
            while self.i < self.code_len and self.code[self.i] in alpha_num:
                tmp += self.code[self.i]
                self.i += 1
            if tmp in keyword:
                self._token_type = 'KEYWORD'
                self._keyword = tmp
            elif tmp.isdecimal():
                self._token_type = 'INT_CONST'
                self._int_val = tmp
            else:
                self._token_type = 'IDENTIFIER'
                self._identifier = tmp

        elif self.code[self.i] in symbol:
            self._token_type = 'SYMBOL'
            self._symbol = self.code[self.i]
            self.i += 1

        elif self.code[self.i] == '\"':
            self.i += 1
            while self.i < self.code_len and self.code[self.i] != '\"':
                tmp += self.code[self.i]
                self.i += 1
            self._token_type = 'STRING_CONST'
            self._string_val = tmp
            self.i += 1

        elif self.code[self.i] == '/':
            if self.code[self.i + 1] == '/':
                self.i += 1
                while self.code[self.i] != '\n':
                    self.i += 1
                self._token_type = ''
            elif self.code[self.i + 1] == '*':
                self.i += 1
                while not(self.code[self.i]=='*' and self.code[self.i + 1]=='/'):
                    self.i += 1
                self.i += 2
                self._token_type = ''
            else:
                self._token_type = 'SYMBOL'
                self._symbol = '/'
                self.i += 1
                
        else:
            self._token_type = ''
            self.i += 1

        if self._token_type == '' and self.has_more_tokens():
            self.advance()

    def token_type(self):
        return self._token_type
    
    def keyword(self):
        return self._keyword

    def symbol(self):
        return self._symbol

    def identifier(self):
        return self._identifier

    def int_val(self):
        return self._int_val

    def string_val(self):
        return self._string_val