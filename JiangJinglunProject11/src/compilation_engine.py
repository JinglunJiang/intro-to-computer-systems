import jack_tokenizer
import symbol_table
import vm_writer

class CompilationEngine():
    def __init__(self, tokenizer: jack_tokenizer.JackTokenizer, vmfile):
        self.jt = tokenizer
        self.vmw = vm_writer.VMWriter(vmfile)
        self.symtbl = symbol_table.SymbolTable()
        self.this_class_name = ''
        self.label_id = 0

        try:
            self.advance()
            self.compile_class()
        except CompileError as e:
            print(e)
        self.vmw.close()

    def advance(self):

        if self.jt.has_more_tokens():
            self.jt.advance()
            return None
        else:
            pass

    def print_token(self):

        if self.jt.token_type() == 'KEYWORD': print('KEYWORD [' + self.jt.keyword() + ']')
        elif self.jt.token_type() == 'SYMBOL': print('SYMBOL [' + self.jt.symbol() + ']')
        elif self.jt.token_type() == 'IDENTIFIER': print('IDENTIFIER [' + self.jt.identifier() + ']')
        elif self.jt.token_type() == 'INT_CONST': print('INT_CONST [' + self.jt.int_val() + ']')
        elif self.jt.token_type() == 'STRING_CONST': print('STRING_CONST [' + self.jt.string_val() + ']')
        else: print('???')
        return None

    def check_symbol(self, symbol, err_msg):

        if self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == symbol:
            self.advance()
        else:
            raise CompileError(err_msg)
        return None

    def get_label_id(self):

        self.label_id += 1
        return self.label_id
    
    def push_var(self, var_name):

        if self.symtbl.kind_of(var_name) == 'argument':
            self.vmw.write_push('argument', self.symtbl.index_of(var_name))
        elif self.symtbl.kind_of(var_name) == 'var':
            self.vmw.write_push('local', self.symtbl.index_of(var_name))
        elif self.symtbl.kind_of(var_name) == 'field':
            self.vmw.write_push('this', self.symtbl.index_of(var_name))
        elif self.symtbl.kind_of(var_name) == 'static':
            self.vmw.write_push('static', self.symtbl.index_of(var_name))
        else:
            raise CompileError('Var Push Error')
        return None
    
    def pop_var(self, var_name):

        if self.symtbl.kind_of(var_name) == 'argument':
            self.vmw.write_pop('argument', self.symtbl.index_of(var_name))
        elif self.symtbl.kind_of(var_name) == 'var':
            self.vmw.write_pop('local', self.symtbl.index_of(var_name))
        elif self.symtbl.kind_of(var_name) == 'field':
            self.vmw.write_pop('this', self.symtbl.index_of(var_name))
        elif self.symtbl.kind_of(var_name) == 'static':
            self.vmw.write_pop('static', self.symtbl.index_of(var_name))
        else:
            raise CompileError('Var Pop Error')
        return None

    def compile_class(self):

        if self.jt.token_type() == 'KEYWORD' and self.jt.keyword() == 'class':
            self.advance()
        else:
            raise CompileError('Class Error 1')

        if self.jt.token_type() == 'IDENTIFIER':
            self.this_class_name = self.jt.identifier()
            self.advance()
        else:
            raise CompileError('Class Error 2')

        self.check_symbol('{', 'Class Error 3')

        self.compile_class_var_dec()

        self.compile_subroutine()

        self.check_symbol('}', 'Class Error 4')

        return None

    def compile_class_var_dec(self):

        while self.jt.token_type() == 'KEYWORD' and self.jt.keyword() in ('static', 'field'):
            kind = self.jt.keyword()
            self.advance()

            if self.jt.token_type() == 'KEYWORD' and self.jt.keyword() in ('int', 'char', 'boolean'):
                type = self.jt.keyword()
                self.advance()
            elif self.jt.token_type() == 'IDENTIFIER':
                type = self.jt.identifier()
                self.advance()
            else:
                raise CompileError('ClassVarDec Error 1')

            if self.jt.token_type() == 'IDENTIFIER':
                self.symtbl.define(self.jt.identifier(), type, kind)
                self.advance()
            else:
                raise CompileError('ClassVarDec Error 2')

            while self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == ',':
                self.advance()
                
                if self.jt.token_type() == 'IDENTIFIER':
                    self.symtbl.define(self.jt.identifier(), type, kind)
                    self.advance()
                else:
                    raise CompileError('ClassVarDec Error 3')

            self.check_symbol(';', 'ClassVarDec Error 4')

        return None

    def compile_subroutine(self):

        while self.jt.token_type() == 'KEYWORD' and self.jt.keyword() in ('constructor', 'function', 'method'):
            self.symtbl.start_subroutine()
            sub_type = self.jt.keyword()
            self.advance()

            if self.jt.token_type() == 'KEYWORD' and self.jt.keyword() in ('void', 'int', 'char', 'boolean'):
                self.advance()
            elif self.jt.token_type() == 'IDENTIFIER':
                self.advance()
            else:
                raise CompileError('SubroutineDec Error 1')
            
            if self.jt.token_type() == 'IDENTIFIER':
                sub_name = self.jt.identifier()
                self.advance()
            else:
                raise CompileError('SubroutineDec Error 2')

            self.check_symbol('(', 'SubroutineDec Error 3')

            if sub_type == 'method':
                self.symtbl.define('this', self.this_class_name, 'argument')

            self.compile_parameter_list()

            self.check_symbol(')', 'SubroutineDec Error 4')

            self.check_symbol('{', 'SubroutineDec Error 5')

            self.compile_var_dec()

            self.vmw.write_function(self.this_class_name + '.' + sub_name, self.symtbl.var_count('var'))

            if sub_type == 'constructor':
                self.vmw.write_push('constant', self.symtbl.var_count('field'))
                self.vmw.write_call('Memory.alloc', 1)
                self.vmw.write_pop('pointer', 0)
            elif sub_type == 'method':
                self.vmw.write_push('argument', 0)
                self.vmw.write_pop('pointer', 0)

            self.compile_statements()

            self.check_symbol('}', 'SubroutineDec Error 6')

        return None

    def compile_parameter_list(self):

        if self.jt.token_type() == 'KEYWORD' and self.jt.keyword() in ('int', 'char', 'boolean'):
            type = self.jt.keyword()
            self.advance()
        elif self.jt.token_type() == 'IDENTIFIER':
            type = self.jt.identifier()
            self.advance()
        else:
            return None

        if self.jt.token_type() == 'IDENTIFIER':
            self.symtbl.define(self.jt.identifier(), type, 'argument')
            self.advance()
        else:
            raise CompileError('ParameterList Error 1')

        while self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == ',':
            self.advance()
    
            if self.jt.token_type() == 'KEYWORD' and self.jt.keyword() in ('int', 'char', 'boolean'):
                type = self.jt.keyword()
                self.advance()
            elif self.jt.token_type() == 'IDENTIFIER':
                type = self.jt.identifier()
                self.advance()
            else:
                raise CompileError('ParameterList Error 2')

            if self.jt.token_type() == 'IDENTIFIER':
                self.symtbl.define(self.jt.identifier(), type, 'argument')
                self.advance()
            else:
                raise CompileError('ParameterList Error 3')

        return None

    def compile_var_dec(self):

        while self.jt.token_type() == 'KEYWORD' and self.jt.keyword() == 'var':
            self.advance()

            if self.jt.token_type() == 'KEYWORD' and self.jt.keyword() in ('int', 'char', 'boolean'):
                type = self.jt.keyword()
                self.advance()
            elif self.jt.token_type() == 'IDENTIFIER':
                type = self.jt.identifier()
                self.advance()
            else:
                raise CompileError('VarDec Error 1')

            if self.jt.token_type() == 'IDENTIFIER':
                self.symtbl.define(self.jt.identifier(), type, 'var')
                self.advance()
            else:
                raise CompileError('VarDec Error 2')

            while self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == ',':
                self.advance()
                
                if self.jt.token_type() == 'IDENTIFIER':
                    self.symtbl.define(self.jt.identifier(), type, 'var')
                    self.advance()
                else:
                    raise CompileError('VarDec Error 3')
        
            self.check_symbol(';', 'VarDec Error 4')

        return None

    def compile_statements(self):

        while self.jt.token_type() == 'KEYWORD' \
            and self.jt.keyword() in ('let', 'if', 'while', 'do', 'return'):
            self.compile_let()
            self.compile_if()
            self.compile_while()
            self.compile_do()
            self.compile_return()

        return None

    def compile_do(self):

        if self.jt.token_type() == 'KEYWORD' and self.jt.keyword() == 'do':
            self.advance()
        else:
            return None
        
        if self.jt.token_type() == 'IDENTIFIER':
            ident = self.jt.identifier()
            self.advance()
        else:
            raise CompileError('DoStatement Error 1')
        
        if self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == '(':

            self.advance()

            self.vmw.write_push('pointer', 0)

            nargs = self.compile_expression_list() + 1

            self.check_symbol(')', 'DoStatement Error 2')
          
            self.vmw.write_call(self.this_class_name + '.' + ident, nargs)

            self.vmw.write_pop('temp', 0)

        elif self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == '.':

            if self.symtbl.kind_of(ident) is None:
                class_name = ident
            else:
                class_name = self.symtbl.type_of(ident)
            
            self.advance()

            if self.jt.token_type() == 'IDENTIFIER':
                sub_name = self.jt.identifier()
                self.advance()
            else:
                raise CompileError('DoStatement Error 3')
            
            self.check_symbol('(', 'DoStatement Error 4')

            if self.symtbl.kind_of(ident) is None:
                nargs = self.compile_expression_list()
            else:
                self.push_var(ident)

                nargs = self.compile_expression_list() + 1

            self.check_symbol(')', 'DoStatement Error 5')
      
            self.vmw.write_call(class_name + '.' + sub_name, nargs)
            self.vmw.write_pop('temp', 0)

        else:
            raise CompileError('DoStatement Error 6')

        self.check_symbol(';', 'DoStatement Error 7')

        return None

    def compile_let(self):

        if self.jt.token_type() == 'KEYWORD' and self.jt.keyword() == 'let':
            self.advance()
        else:
            return None

        if self.jt.token_type() == 'IDENTIFIER':
            var_name = self.jt.identifier()
            self.advance()
        else:
            raise CompileError('LetStatement Error 1')

        if self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == '[':
            self.advance()

            self.compile_expression()

            self.check_symbol(']', 'LetStatement Error 2')

            self.push_var(var_name)

            self.vmw.write_arithmetic('add')

            is_array = True
        else:
            is_array = False

        self.check_symbol('=', 'LetStatement Error 3')

        self.compile_expression()

        self.check_symbol(';', 'LetStatement Error 4')

        if is_array:
            self.vmw.write_pop('temp', 1)
            self.vmw.write_pop('pointer', 1)
            self.vmw.write_push('temp', 1)
            self.vmw.write_pop('that', 0)
        else:
            self.pop_var(var_name)

        return None

    def compile_while(self):

        if self.jt.token_type() == 'KEYWORD' and self.jt.keyword() == 'while':
            self.advance()
            l1 = 'L' + str(self.get_label_id())
            l2 = 'L' + str(self.get_label_id())
        else:
            return None
        
        self.vmw.write_label(l1)

        self.check_symbol('(', 'WhileStatement Error 1')

        self.compile_expression()

        self.check_symbol(')', 'WhileStatement Error 2')

        
        self.vmw.write_arithmetic('not')
        self.vmw.write_if(l2)

        self.check_symbol('{', 'WhileStatement Error 3')

        self.compile_statements()

        self.check_symbol('}', 'WhileStatement Error 4')

        self.vmw.write_goto(l1)
        self.vmw.write_label(l2)

        return None

    def compile_return(self):

        if self.jt.token_type() == 'KEYWORD' and self.jt.keyword() == 'return':
            self.advance()
        else:
            return None

        if self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == ';':
            self.advance()
            self.vmw.write_push('constant', 0)
        else:
            self.compile_expression()

            self.check_symbol(';', 'returnStatement Error 1')

        self.vmw.write_return()
        return None

    def compile_if(self):

        if self.jt.token_type() == 'KEYWORD' and self.jt.keyword() == 'if':
            self.advance()
            l1 = 'L' + str(self.get_label_id())
            l2 = 'L' + str(self.get_label_id())
        else:
            return None

        self.check_symbol('(', 'IfStatement Error 1')

        self.compile_expression()

        self.check_symbol(')', 'IfStatement Error 2')

        self.vmw.write_arithmetic('not')
        self.vmw.write_if(l1)

        self.check_symbol('{', 'IfStatement Error 3')

        self.compile_statements()

        self.check_symbol('}', 'IfStatement Error 4')

        if self.jt.token_type() == 'KEYWORD' and self.jt.keyword() == 'else':
            self.advance()

            self.vmw.write_goto(l2)
            self.vmw.write_label(l1)

            self.check_symbol('{', 'IfStatement Error 5')

            self.compile_statements()

            self.check_symbol('}', 'IfStatement Error 6')

            self.vmw.write_label(l2)

        else:
            self.vmw.write_label(l1)

        return None

    def compile_expression(self):

        self.compile_term()

        while self.jt.token_type() == 'SYMBOL' and self.jt.symbol() in '+-*/&|<>=':
            symbol = self.jt.symbol()
            self.advance()
            self.compile_term()
            
            if symbol == '+': self.vmw.write_arithmetic('add')
            elif symbol == '-': self.vmw.write_arithmetic('sub')
            elif symbol == '*': self.vmw.write_call('Math.multiply', 2)
            elif symbol == '/': self.vmw.write_call('Math.divide', 2)
            elif symbol == '&': self.vmw.write_arithmetic('and')
            elif symbol == '|': self.vmw.write_arithmetic('or')
            elif symbol == '<': self.vmw.write_arithmetic('lt')
            elif symbol == '>': self.vmw.write_arithmetic('gt')
            else: self.vmw.write_arithmetic('eq')

        return None

    def compile_term(self):

        if self.jt.token_type() == 'INT_CONST':
            int_const = int(self.jt.int_val())
            self.vmw.write_push('constant', int_const)
            self.advance()
            
        elif self.jt.token_type() == 'STRING_CONST':
            str_const = self.jt.string_val()
            self.vmw.write_push('constant', len(str_const))
            self.vmw.write_call('String.new', 1)
            for c in str_const:
                self.vmw.write_push('constant', ord(c))
                self.vmw.write_call('String.appendChar', 2)
            self.advance()

        elif self.jt.token_type() == 'KEYWORD' and self.jt.keyword() in ('true', 'false', 'null', 'this'):
            if self.jt.keyword() == 'true':
                self.vmw.write_push('constant', 1)
                self.vmw.write_arithmetic('neg')
            elif self.jt.keyword() == 'false':
                self.vmw.write_push('constant', 0)
            elif self.jt.keyword() == 'null':
                self.vmw.write_push('constant', 0)
            else: 
                self.vmw.write_push('pointer', 0)
            self.advance()

        elif self.jt.token_type() == 'IDENTIFIER':

            ident = self.jt.identifier()
            self.advance()

            if self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == '[':
                self.advance()

                self.compile_expression()

                self.check_symbol(']', 'Term Error 1')

                self.push_var(ident)
                self.vmw.write_arithmetic('add')
                self.vmw.write_pop('pointer', 1)
                self.vmw.write_push('that', 0)

            elif self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == '(':

                self.advance()

                self.vmw.write_push('pointer', 0)

                nargs = self.compile_expression_list() + 1

                self.check_symbol(')', 'Term Error 2')

                self.vmw.write_call(self.this_class_name + '.' + ident, nargs)

            elif self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == '.':

                if self.symtbl.kind_of(ident) is None:
                    class_name = ident
                else:
                    class_name = self.symtbl.type_of(ident)

                self.advance()

                if self.jt.token_type() == 'IDENTIFIER':
                    sub_name = self.jt.identifier()
                    self.advance()
                else:
                    raise CompileError('Term Error 3')
                
                self.check_symbol('(', 'Term Error 4')
                
                if self.symtbl.kind_of(ident) is None:
                    nargs = self.compile_expression_list()
                else:
                    self.push_var(ident)

                    nargs = self.compile_expression_list() + 1

                self.check_symbol(')', 'Term Error 5')

                self.vmw.write_call(class_name + '.' + sub_name, nargs)

            else:

                self.push_var(ident)
                    
        elif self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == '(':

            self.advance()

            self.compile_expression()

            self.check_symbol(')', 'Term Error 6')

        elif self.jt.token_type() == 'SYMBOL' and self.jt.symbol() in '-~':
            symbol = self.jt.symbol()

            self.advance()

            self.compile_term()

            self.vmw.write_arithmetic('neg' if symbol=='-' else 'not')

        else:
            raise CompileError('Term Error')

        return None

    def compile_expression_list(self):

        nargs = 0

        if self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == ')':
            return nargs

        self.compile_expression()
        nargs = 1

        while self.jt.token_type() == 'SYMBOL' and self.jt.symbol() == ',':
            self.advance()
            self.compile_expression()
            nargs += 1

        return nargs
    
class CompileError(Exception):
    pass