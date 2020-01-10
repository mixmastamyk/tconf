'''
    | tconf - TurtleConfig Adapters
    | © 2020, Mike Miller - Released under the LGPL, version 3+.

    Adapt various config sources to a single style of interface.
'''
import os
import logging


log = logging.getLogger(__name__)


class _AttributeDict(dict):
    ''' Access dict items through attributes '''
    def __getattr__(self, attr):
        return self.get(attr)

    __getitem__ = __getattr__


class _Adapter:
    ''' Abstract Base. '''
    def __repr__(self):
        return f'{self.__class__.__name__}({self._source!r})'


class ArgParserAdapter(_Adapter):
    ''' Wraps a TurtleArgumentParser. '''
    def __init__(self, source):
        # parse just once, use Namespace afterward
        self._source = source.parse_args()

    def __getattr__(self, attr_name, **kwargs):
        flattened_name = attr_name.replace('.', '_')
        log.debug('%s.get(%r)', self.__class__.__name__, flattened_name)
        return getattr(self._source, flattened_name, None)

    def __repr__(self):
        return f'{self.__class__.__name__}( {self._source!r} )'


class ConfigParserAdapter(_Adapter):
    ''' Loads values from .ini format files via ConfigParser.
        Note: this supports only one or two levels of hierarchy.
    '''
    def __init__(self, file_path, interpolation=False,
                 default_section=None, **kwargs):
        # defer to avoid loading when not needed:
        from configparser import ConfigParser
        self._copa = ConfigParser(interpolation=interpolation)
        self._copa.read(file_path)
        self._def_sect = default_section
        self._source = file_path

    def __getattr__(self, attr_name):
        log.debug('%s.get(%r)', self.__class__.__name__, attr_name)
        import configparser as cp
        value = None
        section, _, name = attr_name.partition('.')
        if name:  # 2 or more levels
            try:
                value = self._copa.get(section, name)
                log.debug('  found .ini option: [%s] %s = %r',
                          section, name, value)
            except (cp.NoSectionError, cp.NoOptionError) as err:
                log.debug('  ' + str(err))
        else:  # there was only one level this time
            if self._copa.has_section(section):
                value = _AttributeDict(self._copa[section])
            elif self._copa.has_section(self._def_sect):
                # fallback to default
                log.debug('  falling back to [%s]%s', self._def_sect, attr_name)
                value = self._copa[self._def_sect].get(attr_name)
                log.debug('  value: %r %r', value, type(value))
            else:
                pass

        return value


class EnvAdapter(_Adapter):
    ''' Finds values set in the system environment.

        Limitation: Can't find hierarchical values unless used with dict
                    notation.
    '''
    def __init__(self, prefix, env=os.environ, **kwargs):
        self._prefix = prefix
        self._source = env
        self._key = ''

    def __getattr__(self, attr_name):
        key = '.'.join([self._prefix,
                        attr_name.upper()])
        log.debug('%s.get(%r)', self.__class__.__name__, key)

        value = self._source.get(key)
        if value is not None:
            log.info('  found environment variable: %r %r', key, value)
        else:
            log.debug('  not found in environment.')

        return value

    def __repr__(self):
        return f'{self.__class__.__name__}(os.environ)'


class JSONAdapter(_Adapter):
    ''' Loads values from JSON format files. '''
    def __init__(self, file_path, **kwargs):
        from json import load  # defer to avoid loading when not needed
        with open(file_path) as f:
            self._data = load(f, object_hook=_AttributeDict)
        self._source = file_path

    def __getattr__(self, attr_name):
        log.debug('%s.get(%r)', self.__class__.__name__, attr_name)
        value = self._data

        for segment in attr_name.split('.'):  # crawl down
            value = getattr(value, segment, None)
            log.debug('  segment: %r, value: %r', segment, value)
            if value is None:
                break

        return value


class ObjectAdapter(_Adapter):
    ''' Load values from objects. '''
    def __init__(self, source):
        self._source = source

    def __getattr__(self, attr_name, **kwargs):
        log.debug('ObjectAdapter.get attr_name: %r', attr_name)
        value = self._source
        for segment in attr_name.split('.'):  # crawl down
            value = getattr(value, segment, None)
            log.debug('  segment: %r, val: %r', segment, value)
            if value is None:
                break

        if value is not None:
            if isinstance(value, type):  # is class type
                log.debug('  class found: %r', value)
                value = self.__class__(value)
            log.debug('  found: %s=%r', attr_name, value)
        else:
            log.debug('  not found in object.')

        return value

    def __repr__(self):
        return f'{self.__class__.__name__}({self._source.__name__})'


class SYAMLAdapter(_Adapter):
    ''' Loads values from YAML format files. '''
    def __init__(self, file_path, **kwargs):
        import strictyaml  # defer to avoid loading when not needed
        with open(file_path) as f:
            self._data = strictyaml.load(f.read())
        self._yaml_type = strictyaml.YAML
        self._source = file_path

    def __getattr__(self, attr_name):
        value = self._data  # start here
        log.debug('%s.get(%r)', self.__class__.__name__, attr_name)

        for segment in attr_name.split('.'):  # crawl down
            value = value.get(segment)
            log.debug('  segment: %r, value: %s', segment, value)
            if value is None:
                break
            elif isinstance(value, self._yaml_type):
                try:
                    value = _AttributeDict(value.data)
                except ValueError:
                    value = value.data
                    log.info('  found yaml option: %s: %r', segment, value)

        return value


class XMLAdapter(_Adapter):
    ''' Loads values from XML format files and directs access.

        Note: skips root element to provide parity with other source types.
    '''
    def __init__(self, file_path, attr_prefix='_', **kwargs):
        import xmltodict  # defer to avoid loading when not needed
        with open(file_path) as f:
            data = xmltodict.parse(
                f.read(), xml_attribs=True, attr_prefix=attr_prefix,
                disable_entities=False,
            )
        if len(data) == 1:  # skip root
            data = tuple(data.values())[0]
        self._data = data
        self._source = file_path

    def __getattr__(self, attr_name):
        from collections import OrderedDict
        value = _AttributeDict(self._data)

        for segment in attr_name.split('.'):  # crawl down
            value = getattr(value, segment, None)
            log.debug('segment: %r, value: %r', segment, value)
            if value is None:
                break
            elif isinstance(value, OrderedDict):  # no object_hook
                value = _AttributeDict(value)
                # needs to crawl for more OrderedDicts
        return value


file_adapter_map = {
    '.ini': ConfigParserAdapter,
    '.json': JSONAdapter,
    '.xml': XMLAdapter,
    '.yml': SYAMLAdapter,
    '.yaml': SYAMLAdapter,
}
