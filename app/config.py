import os
from ConfigParser import SafeConfigParser


class Parser(SafeConfigParser, object):
    def __init__(self, *args, **kwargs):
        object.__init__(self)
        SafeConfigParser.__init__(self, *args, **kwargs)
        self.__path = None
        self.__last_updated = None

    def read(self, file_name):
        super(Parser, self).read(filenames=file_name)
        self.__path = file_name
        self.__last_updated = None

    def _reload(self):
        last_updated = os.path.getmtime(self.__path)
        if last_updated != self.__last_updated:
            super(Parser, self).read(self.__path)
            self.__last_updated = last_updated

    def get(self, *args, **kwargs):
        self._reload()
        return super(Parser, self).get(*args, **kwargs)

    def getboolean(self, *args, **kwargs):
        self._reload()
        return super(Parser, self).getboolean(*args, **kwargs)

    def getint(self, *args, **kwargs):
        self._reload()
        return super(Parser, self).getint(*args, **kwargs)


class Config(object):

    PATHS = {
        'core': os.environ.get('QFI_CORE_INI') or 'core.ini',
        'alembic': 'alembic.ini'
    }

    ABSPATHS = {
        'core': None,
        'alembic': None
    }

    core = None
    alembic = None

    @classmethod
    def init(cls):
        for name, file_name in cls.PATHS.iteritems():
            dir_path = os.environ.get('QFI_CONFIG_PATH', os.path.expanduser('~/.config/qfi'))
            path = os.path.join(dir_path, file_name)
            if not os.path.exists(path):
                continue
            parser = Parser()
            parser.read(path)
            setattr(cls, name, parser)
            cls.ABSPATHS[name] = path

    @classmethod
    def generate(cls):
        for name, file_name in cls.PATHS.iteritems():
            dir_path = os.environ.get('QFI_CONFIG_PATH', os.path.expanduser('~/.config/qfi'))
            path = os.path.join(dir_path, file_name)
            parser = Parser()
            env_has_config = False
            for k in filter(lambda x: x.startswith('QFI_CONF__%s' % name), os.environ):
                sect, key = k.replace('QFI_CONF__%s__' % name, '').split('__')
                val = os.environ.get(k).strip('"')
                if not parser.has_section(sect):
                    parser.add_section(sect)
                parser.set(sect, key, val)
                if not env_has_config:
                    env_has_config = True

            if env_has_config:
                with open(path, 'wb') as fd:
                    parser.write(fd)

Config.init()
