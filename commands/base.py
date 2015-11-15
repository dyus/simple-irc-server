class BaseCommand:
    def parse_command(self):
        raise NotImplemented()

    def run_command(self):
        raise NotImplemented()

    @staticmethod
    def concat_after_colon(args):
        """
        Метод объединяет аргументы после :
        Пример ['PRIVMSG', '#room', ':first', 'msg'] -> ['PRIVMSG', '#room', ':first msg']
        :param args:
        :return:
        """
        indexes = [n for n, arg in enumerate(args) if arg.startswith(':')]
        if indexes:
            args[indexes[0]:] = ' '.join(args[indexes[0]:])