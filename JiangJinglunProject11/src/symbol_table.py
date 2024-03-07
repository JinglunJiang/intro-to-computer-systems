class SymbolTable():
    
    def __init__(self):
        self.class_symtbl = []
        self.sub_symtbl = []
        self.static_index_max = -1
        self.field_index_max = -1
        self.argument_index_max = -1
        self.var_index_max = -1

    def start_subroutine(self):
        self.sub_symtbl = []
        self.argument_index_max = -1
        self.var_index_max = -1

    # kindの値について、本来はenum型を使うべきだが手抜きで文字列にしている
    def define(self, name, type, kind):
        if kind == 'static':
            self.static_index_max += 1
            self.class_symtbl.append(
                {
                    'name': name,
                    'type': type,
                    'kind': kind,
                    'index': self.static_index_max
                }
            )
        elif kind == 'field':
            self.field_index_max += 1
            self.class_symtbl.append(
                {
                    'name': name,
                    'type': type,
                    'kind': kind,
                    'index': self.field_index_max
                }
            )
        elif kind == 'argument':
            self.argument_index_max += 1
            self.sub_symtbl.append(
                {
                    'name': name,
                    'type': type,
                    'kind': kind,
                    'index': self.argument_index_max
                }
            )
        elif kind == 'var':
            self.var_index_max += 1
            self.sub_symtbl.append(
                {
                    'name': name,
                    'type': type,
                    'kind': kind,
                    'index': self.var_index_max
                }
            )
        else:
            pass

        return None

    def var_count(self, kind):
        if kind == 'static':
            return self.static_index_max + 1
        elif kind == 'field':
            return self.field_index_max + 1
        elif kind == 'argument':
            return self.argument_index_max + 1
        elif kind == 'var':
            return self.var_index_max + 1
        else:
            return 0

    def kind_of(self, name):
        for sym in self.class_symtbl:
            if sym['name'] == name:
                return sym['kind']

        for sym in self.sub_symtbl:
            if sym['name'] == name:
                return sym['kind']
        return None

    def type_of(self, name):
        for sym in self.class_symtbl:
            if sym['name'] == name:
                return sym['type']

        for sym in self.sub_symtbl:
            if sym['name'] == name:
                return sym['type']

        return None

    def index_of(self, name):
        for sym in self.class_symtbl:
            if sym['name'] == name:
                return sym['index']

        for sym in self.sub_symtbl:
            if sym['name'] == name:
                return sym['index']

        return 0

    # 以下デバッグ用
    def print_cls_symtbl(self):
        print('---------------------------')
        print('<class>\nname\ttype\tkind\tindex')
        for item in self.class_symtbl:
            print(item['name'], item['type'], item['kind'], item['index'])
        print('---------------------------')

    def print_sub_symtbl(self):
        print('---------------------------')
        print('<sub>\nname\ttype\tkind\tindex')
        for item in self.sub_symtbl:
            print(item['name'], item['type'], item['kind'], item['index'])
        print('---------------------------')

    