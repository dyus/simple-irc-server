# coding: utf-8

class Message:
    def __init__(self, prefix, command, *args):
        self.prefix = prefix
        self.command = command
        self.params = [arg for arg in args if arg is not None]

    def __str__(self):
        params = self.params

        if len(params) > 0 and ' ' in params[-1]:
            params[-1] = ':%s' % params[-1]

        return '{prefix}{command} {params}\r\n'.format(
            prefix=':%s ' % self.prefix if self.prefix is not None else '',
            command=str(self.command),
            params=' '.join(params)
        )

    def __bytes__(self):
        return self.__str__().encode('utf-8')
