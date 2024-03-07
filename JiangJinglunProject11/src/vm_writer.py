'''
演算 : add, sub, neg, eq, gt, lt, and, or, not
メモリセグメント : argument, local, static, constant, this, that, pointer, temp
push, pop, label, goto, if-goto, function, call, return

'''


class VMWriter():
    def __init__(self, vmfile):
        self.vmf = open(vmfile, mode='w')
    
    def write_push(self, segment, index):
        if segment in ('argument', 'local', 'static', 'constant', 'this', 'that', 'pointer', 'temp'):
            self.vmf.write(f'push {segment} {index}\n')
        return None

    def write_pop(self, segment, index):
        if segment in ('argument', 'local', 'static', 'constant', 'this', 'that', 'pointer', 'temp'):
            self.vmf.write(f'pop {segment} {index}\n')
        return None
    
    def write_arithmetic(self, command):
        if command in ('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'):
            self.vmf.write(f'{command}\n')
        return None

    def write_label(self, label):
        self.vmf.write(f'label {label}\n')
        return None

    def write_goto(self, label):
        self.vmf.write(f'goto {label}\n')
        return None

    def write_if(self, label):
        self.vmf.write(f'if-goto {label}\n')
        return None 

    def write_call(self, name, nargs):
        self.vmf.write(f'call {name} {nargs}\n')
        return None

    def write_function(self, name, nlocals):
        self.vmf.write(f'function {name} {nlocals}\n')
        return None
    
    def write_return(self):
        self.vmf.write(f'return\n')
        return None

    def close(self):
        self.vmf.close()
        return None