import logging
LOG = logging.getLogger('server')


class IP:
    def __set__(self, instance, value):
        ip_str = value.split('.')
        if len(ip_str) != 4:
            LOG.critical(f'Некорректно указан IP адрес: {value}')
            exit(1)
        for el in ip_str:
            if not el.isdigit() and 0 < int(el) < 256:
                LOG.critical(f'Некорректно указан IP адрес: {value}')
                exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
