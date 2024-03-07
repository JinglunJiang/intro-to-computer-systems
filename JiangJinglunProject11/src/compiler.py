import sys
import os

import jack_tokenizer
import compilation_engine

def main():
    jackfilepath = sys.argv[1]
    
    if os.path.isdir(jackfilepath):
        if jackfilepath[-1] == '/':
            jackfilelist = [jackfilepath + _ for _ in os.listdir(jackfilepath) if _[-5:]=='.jack']
        else:
            jackfilelist = [jackfilepath + '/' + _ for _ in os.listdir(jackfilepath) if _[-5:]=='.jack']
    elif os.path.isfile(jackfilepath) and jackfilepath[-5:]=='.jack':
        jackfilelist = [jackfilepath]
    else:
        print('Error')
        return

    for jackfile in jackfilelist:
        vmfile = jackfile[:-5] + '.vm'
        compilation_engine.CompilationEngine(
            jack_tokenizer.JackTokenizer(jackfile),
            vmfile
        )


if __name__ == '__main__':
    main()