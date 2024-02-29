import os
from Tokenizer import tokens
from Parser import Parser

def remove_comments(lines):
    without_comments = []
    in_block_comment = False

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        new_line, in_block_comment = process_line(line, in_block_comment)
        if new_line:
            without_comments.append(new_line)
    
    return without_comments

def process_line(line, in_block_comment):
    new_line = []
    i = 0
    while i < len(line):
        if not in_block_comment and line[i:i+2] == '/*':
            in_block_comment = True
            i += 2
        elif in_block_comment and line[i:i+2] == '*/':
            in_block_comment = False
            i += 2
        elif not in_block_comment and line[i:i+2] == '//':
            break
        elif not in_block_comment:
            new_line.append(line[i])
            i += 1
        else:
            i += 1

    return ''.join(new_line).strip(), in_block_comment

def file_pipeline(directory):
    output_folder = os.path.join(directory, 'new_xml_code')
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(directory):
        if filename.endswith('.jack'):
            process_file(directory, filename, output_folder)

def process_file(directory, filename, output_folder):
    filepath = os.path.join(directory, filename)
    with open(filepath) as f:
        jack_code = remove_comments(f.readlines())

    base_filename = filename[:-5]
    output_txml_path = os.path.join(output_folder, f'{base_filename}T.xml')
    output_xml_path = os.path.join(output_folder, f'{base_filename}.xml')

    tokenize_xml_str, tokenize_xml_lst = tokens(jack_code)
    write_to_file(output_txml_path, tokenize_xml_str)

    parser = Parser(tokenize_xml_lst)
    parsed_output = parser.parse()
    write_to_file(output_xml_path, parser.output)

def write_to_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_pipeline(sys.argv[1])
    else:
        print("Usage: python script.py <directory path>")