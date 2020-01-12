'''
    | tconf - TurtleConfig - It's turtles all the way down…
    | © 2020, Mike Miller - Released under the LGPL, version 3+.
'''
import logging
import os
from argparse import ArgumentParser
from ast import literal_eval
from collections.abc import Sequence
from os.path import abspath, dirname, exists
from types import ModuleType
from typing import get_type_hints, _GenericAlias, _SpecialForm

from typeguard import check_type

from . import adapters, meta
from .adapters import file_adapter_map


log = logging.getLogger(__name__)


class DefaultsMissingError(RuntimeError):
    ''' Defaults not found, one must be passed in the source argument sequence. '''


class TurtleConfig:
    ''' A configuration object that retrieves parameters from a number of
        sources, in the order given.
    '''
    _env_prefix = 'PY'

    def __init__(self, app_name, sources,
                 ensure_paths=False,
                 env_prefix=None,
                 ini_default_section='main',
                 ini_interpolation=None,
                 vendor_name=None,
                ):
        log.debug('🐢 TurtleConfig, version: %r', meta.version)
        if not isinstance(sources, Sequence):
            raise ValueError('A sequence of sources is required.')

        self._app_name = app_name
        self._ini_default_section = ini_default_section
        self._ini_interpolation = ini_interpolation
        self._types_cache = {}
        self._values_cache = {}
        self._vendor_name = vendor_name
        if env_prefix:
            self._env_prefix = env_prefix

        # wrap sources with Adapters
        self._sources = []
        for source in sources:
            if isinstance(source, str):
                source = self._handle_path(source, ensure_paths)
            wrapped = self._adapt_source(source)
            if wrapped is not None:
                self._sources.append(wrapped)
            log.debug('  source: %r', wrapped)

        # find the defaults object, likely bringing up the rear:
        for obj in reversed(self._sources):
            if isinstance(obj, adapters.ObjectAdapter):
                self._types_cache = { p[0]: p[2]  # dump value
                                      for p in _list_object_props(obj._source) }
                break  # -en Sie
        else: # no break, aka not found
            raise DefaultsMissingError(DefaultsMissingError.__doc__)

    def __getattr__(self, attr_name):
        ''' Attribute-style interface: cfg.foo.bar.baz.

            Only called when self.attr doesn't exist.
        '''
        if attr_name in self._values_cache:
            return self._values_cache[attr_name]
        value = None
        log.debug('🐢.get(%r)', attr_name)

        # find value
        for source in self._sources:  # find the value
            value = getattr(source, attr_name)
            if value is not None:
                break  # found something
        else:  # not broken, not found
            raise AttributeError('%r not found.' % attr_name)

        # fix attr_name if used with default section in ConfigParser
        # This is very complicated, would like to remove this:
        if ('.' not in attr_name
            and isinstance(source, adapters.ConfigParserAdapter)
            and source._def_sect
            and not isinstance(value, adapters._AttributeDict)):
                attr_name = source._def_sect + '.' + attr_name

        # potentially convert then type check value
        dest_type = self._types_cache.get(attr_name)
        if isinstance(value, str) and dest_type is not str:
            # strings may or may not need type coercion
            value = self._coerce_string(attr_name, value, dest_type)

        elif isinstance(value, adapters.ObjectAdapter):
            return value  # needed for attr iface :-/

        if isinstance(value, adapters._AttributeDict):  # very inefficient,
            # checks/converts whole section to support the attr iface :-/
            for key, val in value.items():  # every one !
                key_name = attr_name + '.' + key
                dest_type = self._types_cache.get(key_name)
                if isinstance(val, str) and dest_type is not str:
                    value[key] = self._coerce_string(key_name, val, dest_type)
                check_type(key_name, value[key], dest_type)
        else: # everything else
            check_type(attr_name, value, dest_type)

        self._values_cache[attr_name] = value
        return value

    def __getitem__(self, attr_path):
        ''' Dictionary style interface: cfg['foo.bar.baz'].

            TODO: make this the main implementation.
        '''
        try:
            return self.__getattr__(attr_path)
        except AttributeError as err:
            raise KeyError(str(err)) from err

    def _adapt_source(self, source):
        ''' Wrap a source with an Adapter class. '''
        if isinstance(source, adapters._Adapter):   # not again!
            pass
        elif isinstance(source, str):               # a path
            pth = source
            source = None
            if os.access(pth, os.R_OK):  # avoid non-existent | unreadable file
                _, ext = os.path.splitext(pth)
                AdapterClass = file_adapter_map.get(ext.casefold())
                if AdapterClass:
                    source = AdapterClass(pth,
                        interpolation=self._ini_interpolation,
                        default_section=self._ini_default_section,
                    )
            else:
                log.warn('file %r unreadable, skipping.', pth)

        elif source in (os.environ, os.environb):
            prefix = self._env_prefix + '_' + self._app_name.upper()
            source = adapters.EnvAdapter(prefix, env=source)

        elif isinstance(source, TurtleArgumentParser):
            source = adapters.ArgParserAdapter(source)

        elif isinstance(source, (type, ModuleType)):  # is class or module
            source = adapters.ObjectAdapter(source)

        else:
            raise NotImplementedError('Source %r not recognized.' % source)

        return source

    def _coerce_string(self, attr_name, value, type_):
        ''' Convert a string value to the expected type. '''
        if isinstance(type_, dict):  # retrieve from argparse kwargs
            type_ = type_.get('type')

        if type_ is not None:
            if type_ is bool:
                converted = value.casefold() in ('true', '1')

            # compound types will need a harder look:
            elif (type_ in (list, dict, set, tuple) or
                  isinstance(type_, (_GenericAlias, _SpecialForm)) # __origin__
                ):  # a safer, limited eval, raises (ValueError, SyntaxError)
                converted = literal_eval(value)

            elif type_ is type(None):  # type_ is NoneType  :-/
                if value is None or value.casefold() in ('null', 'none'):
                    converted = None

            else:  # simple types: int, float, …
                converted = type_(value)

            log.debug('coercing value from: %r to %r', value, converted)
            value = converted

        return value

    def _handle_path(self, path_str, ensure_paths=False):
        ''' Render an absolute path with folders from appdirs,
            and optionally ensure file exists.
        '''
        if path_str.startswith('{'):  # try to render template
            from appdirs import site_config_dir, user_config_dir
            sd = site_config_dir(self._app_name, self._vendor_name)
            ud = user_config_dir(self._app_name, self._vendor_name)
            path_str = path_str.format(site_config_dir=sd, user_config_dir=ud)

        if ensure_paths:
            folder_exists = None  # these are separate, to create relative file
            folder = dirname(path_str)
            # avoid attempt to create own folder:
            if folder in ('', '.'):  # current dir
                folder_exists = True
            else:
                log.debug('ensuring %r', path_str)
                try:
                    os.makedirs(folder, exist_ok=True)
                    folder_exists = True
                except OSError as err:
                    log.warn('unable to create path: %s', str(err))

            if folder_exists:
                try:
                    if not exists(path_str):  # race
                        open(path_str, 'a').close()
                except OSError as err:
                    log.warn('unable to create file: %s', str(err))

        if not path_str.startswith('/'):  # relative?
            if len(path_str) > 2 and path_str[1] == ':':
                pass  # Winders, nope
            else:
                path_str = abspath(path_str)
        return path_str

    def add_turtle_source(self, source):
        ''' After the fact. '''
        if not isinstance(source, adapters._Adapter):
            source = self._adapt_source(source)
        self._sources = self._sources + (source,)

    def clear_turtle_cache(self):
        ''' Use to update variables after a config update, or free memory. '''
        self._values_cache.clear()


class TurtleArgumentParser(ArgumentParser):
    ''' An ArgumentParser that is automatically populated by TurtleConfig.

        Arguments:
            app_defaults:  a (class, module, object) containing data.
            help_templ: a string such as: '🐢 {description} ({type_str})'
    '''
    def __init__(self, app_defaults, *args, help_templ=None, **kwargs):

        super().__init__(*args, **kwargs)
        if not help_templ:
            help_templ = '🐢 {description} ({type_str})'

        # look over default object and configure argument details:
        for key, value, annotation in _list_object_props(app_defaults, mod_name=1):

            log.debug('TurtleArgumentParser arg: %r', (key, value, annotation))
            params = {}
            if type(annotation) is dict:
                description = annotation.pop('desc', '')
                type_ = annotation.pop('type', value.__class__)
                params = annotation  # pass rest to parser.add_argument()
            else:
                type_, description = value.__class__, ''
            type_str = type_.__name__ if hasattr(type_, '__name__') else str(type_)

            if value is False:
                params['action'] = 'store_true'
                type_str = 'False, sets True'
            elif value is True:
                params['action'] = 'store_false'
                type_str = 'True, sets False'
            else:
                params['metavar'] = type_str[0].upper()
                params['type'] = type_

            if type(annotation) is dict and 'choices' in annotation:
                type_str += ': ' + str(annotation['choices'])[1:-1]

            # specific help value overrides
            if 'help' not in params:
                params['help'] = help_templ.format(
                    description=description,
                    type_str=type_str,
                )
            # build argument
            self.add_argument(
                (self.prefix_chars[0]*2) + key,
                default=None, # don't want to stop here, continue with None
                **params,
            )


def _list_object_props(container, prefix='', mod_name=False):
    ''' Inspect object property annotations and types, return a list.

        Arguments:
            container:  the object to inspect
            prefix:     keeps track of where we are in tree
            mod_name:   use argparse style names instead of obect notation.
    '''
    annos = get_type_hints(container)
    arg_list = []
    if prefix:
        if mod_name:
            prefix = prefix + '-'
        else:
            prefix = prefix + '.'

    for key, value in vars(container).items():
        if key.startswith('_'):
            continue

        annotation = annos.get(key)
        if mod_name:
            arg_name = prefix + key.replace('_', '-')
        else:
            arg_name = prefix + key

        if isinstance(value, type):  # class, follow container
            arg_list.extend(_list_object_props(value, prefix=arg_name))
        else:
            if annotation:
                arg_list.append( (arg_name, value, annotation) )
            else:  # None, fall back to type of value
                arg_list.append( (arg_name, value, type(value)) )

    return arg_list
