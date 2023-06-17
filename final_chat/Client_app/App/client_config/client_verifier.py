import dis


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                res = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for el in res:
                    if el.opname == 'LOAD_GLOBAL':
                        if el.argval not in methods:
                            methods.append(el.argval)

        for command in ('accept', 'listen'):
            if command in methods:
                raise TypeError(
                    f'В классе Client обнаружено использование запрещенного метода - {command}')
        super().__init__(clsname, bases, clsdict)
