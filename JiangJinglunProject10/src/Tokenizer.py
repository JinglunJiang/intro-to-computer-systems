import re

pattern = re.compile("(\{|\}|\(|\)|\[|\]|\.|\,|\;|\+|\-|\*|\/|\&|\||\<|\>|\=|\~| )")
keyword = {
    'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
    'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'}
symbol = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}
xml_symbol = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}

# Function used to add the <tokens> </tokens> tag
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
    xml_output = [] # For the convenience of the parser
    code_words = re.split(pattern, code_line)
    in_string = False # Flag to see if is currently inside a string constant
    for word in code_words:
        if len(word) != 0:
            # Coping with the string constants
            if in_string == True:
                if word[-1] == '"':
                    in_string = False
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
                    in_string = True
                    string_constant = word[1:]

            # If it is not a string constant
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