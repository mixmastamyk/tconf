
…🐢⻳   TurtleConfig   ⻳🐢…
=============================

*Why yes, it's turtles all the way down 🐢🐢🐢🐢…*

This is an attempt at a cascading configuration library that I'd like to use.
The basic idea is that you get a configuration object and read its properties for the
values of options you've defined all over the place, haha.

Behind the scenes TurtleConfig will potentially look at command-line
parameters,
the environment,
user configuration files,
host/site configuration,
and the app's own defaults to find the best value.
Typically in that order,
although you're welcome to modify that list of configuration sources to
whatever you see fit.

Instead of the typical hodge-podge of custom code needed for that,
setting up "TC" looks a little something like this:

.. code-block:: python

    import os
    from tconf import TurtleConfig

    # First, define your application schema/defaults:
    import config as AppDefaults  # via module, or

    # a class/object, which is easier to view here:
    class AppDefaults:
        an_option = True  # simple options

        class main:  # or perhaps a hierarchy
            jpeg_quality = 95
            file_path = '/foo'

    # Next, create a TurtleConfig object:
    cfg = TurtleConfig(
        'AppyMcApp',    # the app's name
        sources = (     # a list of option sources
            os.environ,
            '{user_config_dir}/options.ini',    # appdirs
            '{site_config_dir}/options.ini',    # appdirs
            '/path/to/options.xml',  # or JSON, YAML, etc.
            AppDefaults,                        # defaults
        ),
        ensure_paths=True,  # creates folders/files when needed
    )

**Virtual Paths**

The ``user_config_dir`` & ``site_config_dir`` variables above are provided by
the
`appdirs <https://pypi.org/project/appdirs/>`_ module
so you don't have to worry about cross platform locations—\
unless you want to.

Tip:  You may want to start logging at ``DEBUG`` level before loading TC,
as it helps to visualize what is going on underneath its shell.
The
`out <https://pypi.org/project/out/>`_ module
is perhaps the easiest way to do that:

.. code-block:: python

    import sys, out
    out.configure(level='debug' if '-d' in sys.argv else 'info')


Try It!
--------

First, install the tiny, pure-python package:

.. code-block:: shell

    ⏵ python3 -m pip install tconf

And off you go.
There are two interfaces to get at options,
via attributes or dictionary-like access:

.. code-block:: python

    # Attribute interface
    >>> cfg.main.jpeg_quality
    95

    # Dictionary interface
    >>> cfg['main.jpeg_quality']
    95


Now, why would you use one form over the other?

Well, the first (attribute interface) is easier to type, read,
and the design I originally wanted.
However, it has limitations in a number of circumstances that are damn near
impossible to overcome,
which you'll read about below.

So the second (dictionary form) is generally preferred unless the app has
simple needs,
such as a single-level configuration.
An editor "snippet" can mitigate the extra keystrokes.


Value Types
~~~~~~~~~~~~~~

Some configuration sources are limited (in a good way)† in that they return
option values only as strings.
For example, the environment, strict yaml, and ``.ini`` files have string-only
values.
However, our app is likely to need real types,
such as integers, booleans, or lists of strings, etc.
What to do?

Under TC,
the types of option values are assumed to be the same type as their default
values,
which are defined in Python.
Remember, defaults are found from the last class/module/object passed as a
source,
the ``AppDefaults``
object as seen in the example above.
Think of your ``AppDefaults`` as a schema for configuration data.

The default value types may be annotated,
otherwise the given default will be inspected for its type as a fallback.
This means you can skip having to write type annotations much of the time
as they are inferred.

**Points of interest:**

- Turtle will attempt to convert or "coerce" string values gathered from a
  config source into the expected (annotated or inferred) non-string type.

- Values are then type checked via the
  `typeguard <https://pypi.org/project/typeguard/>`_ module.

- Currently, simple and compound Python types are supported:

  - ``str, int, float, bool``
  - ``list, tuple, dict, set``
  - ``List, Tuple, Sequence, Dict, Set`` *(from le typing module)*
  - ``Union, Any, Optional, etc.`` *(ditto)*

- Annotations become more useful with complex compound types defined with the
  stdlib typing module.

- Compound types should be encoded in strings with Python syntax if you'd like
  them decoded automatically.
  Otherwise, pass them as strings and decode them yourself.

  - If you're using an already typed (via syntax) file format such as JSON,
    don't do this,
    rather spread the data structure out as normal.

- Annotations may also support kwargs for an ArgumentParser, see below.

† Conversion of types is better done in the application-layer than in the file
format to avoid unexpected edge-case bugs like
`"the Norway problem." <https://hitchdev.com/strictyaml/why/implicit-typing-removed/>`_


Configuration Sources
-----------------------

Each configuration source has an Adapter class to integrate their various
different interfaces into one.
As mentioned,
when looking for options,
the sources are searched in order from front to back,
top to bottom until a suitable value is found.
If an option is not found in any source,
an ``AttributeError`` or ``KeyError`` is raised to ensure bugs are found early.


Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~

Perhaps you'd like to override options with environment variables.
This is what it will look like:

.. code-block:: python

    >>> os.environ['PY_APPYMCAPP.MAIN.JPEG_QUALITY'] = '94'
    >>> cfg['main.jpeg_quality']
    94

A matching environment variable is in uppercase and is prefixed with
``PY_`` and the application name.
Both parts of the prefix are able to be modified by modifying the app_name
and/or passing an
``env_prefix='…'`` to the ``TurtleConfig`` constructor.


**Limitations:**

Due to limits with how the environment adapter works,
it cannot provide hierarchical access to settings via the attribute interface.

The reason is that the attributes are evaluated left to right.
The object doesn't yet have enough information to know if it should return the
final value or continue down the attribute chain.
It can either do one or the other,
leading to a number of broken cases from either decision.
Bare attributes *do* work with the environment when options are kept to a
single-level however.
As mentioned,
dictionary-style access works consistently on the other hand.


ConfigParser
~~~~~~~~~~~~~~

``.ini`` files have two levels by design and are great for config files.
Therefore they do work hierarchically by default and would typically require
exactly two levels.

There is one exception for convenience, however.
If there is a single-level option name given,
the section ``[main]`` (configurable also) is tried as a fallback.
This is so one can use a single-level as well as a dual-level config with
ConfigParser,
simply by putting root options under ``[main]``:

.. code-block:: shell

    ⏵ cat test.ini
    [main]
    jpeg_quality = 96
    # snip

.. code-block:: python

    >>> cfg.main.jpeg_quality
    96
    >>> cfg['main.jpeg_quality']
    96
    >>> cfg.jpeg_quality  # looks in [main] also
    96


JSON
~~~~~~~~~~~~~~

JSON is not a great format for humans to edit,
but still relatively common as configuration:


.. code-block:: shell

   ⏵ cat test.json
    {   "an_option": true,
        "main": {
            "jpeg_quality": 96,
    # ~snip~

.. code-block:: python

    >>> cfg.main.jpeg_quality
    96
    >>> cfg['main.jpeg_quality']
    96
    >>> cfg.does_not_exist
    # …
    AttributeError: 'does_not_exist' not found.

    >>> cfg.an_option
    True

Compound data types are better encoded in the JSON itself
rather than trying to smash "PyON" into strings.


XML
~~~~~~~~~~~~~~

Requires
`xmltodict <https://hitchdev.com/xmltodict/>`_:

.. code-block:: shell

   ⏵ pip3 install tconf[xml]  # or
   ⏵ pip3 install xmltodict

   ⏵ cat test.xml
    <?xml version="1.0" encoding="UTF-8"?>
    <root>
        <an_option>true</an_option>
        <a_null2/>
        <main>
            <jpeg_quality>96</jpeg_quality>
    # ~snip~

.. code-block:: python

    >>> cfg.main.jpeg_quality
    96
    >>> cfg['main.jpeg_quality']
    96
    >>> cfg.a_null2
        # implied None
    >>> cfg.an_option
    True


This Adapter is kinda weak so far,
could use a rewrite.

**Limitations:**

- Throws out the root element for parity with other source types.

- Finds only the first node (tag) at each level due to a dictionary-like
  implementation.

- XML attributes are not currently reachable.  :-/


Strict YAML
~~~~~~~~~~~~~~

A much safer, simpler subset of YAML, which requires the
`strictyaml <https://hitchdev.com/strictyaml/>`_
module:

.. code-block:: shell

   ⏵ pip3 install tconf[yaml]  # or
   ⏵ pip3 install strictyaml

   ⏵ cat test.yaml
    an_option: true
    a_null: null

    main:
        jpeg_quality: 96
    # snip

See JSON above for similar Python snippet.


Others
~~~~~~~~~~~~~~

It's trivial to add an adapter for other sources and file formats.
First subclass ``adapters._Adapter`` and add an instance to the sources list.
There is an ``file_adapter_map`` in the adapters module root to register file
extensions to avoid having to pass an instance every time, if desired.

Tip: Additionally,
passing adapters into the source list manually can also be used to give an
Adapter different arguments than it would normally get.

*"Use the source, Luke!"*


ArgumentParser
~~~~~~~~~~~~~~~~

You may have been thinking, what about the command-line?
Good news,
there's an ArgumentParser subclass available if you'd like all options
presented auto-magically.
Types and parameters are passed to ArgumentParser through annotations of the
``AppDefaults`` object:

.. code-block:: python

    # appy.py
    from tconf import TurtleConfig, TurtleArgumentParser # 👀

    class AppDefaults:
        # ~snip~
        class main:
            # how to add a type via annotation,
            # simple types are already detected however:
            jpeg_quality: int = 95

            # Also use annotations to pass a dictionary of
            # kwargs to ArgParser, w/o descriptive help text:
            jpeg_quality: dict(  # 👀
                type=int,
                desc='The jpeg quality level',
            ) = 95

    tcfg = TurtleConfig(
        'AppyMcApp',
        sources = (
            TurtleArgumentParser(AppDefaults),  # 👀
            # environment, config files, etc…
            AppDefaults,
        ),
        ensure_paths=True,
    )


Give it a try:

.. code-block:: shell

   ⏵ appy.py -h

    usage: appy.py [-h] [--a-simple-option] [--main-jpeg-quality I]
                   [--main-sync-dates-to-filesystem] [--main-work-in-place]
                   [--rotate-resample S] [--sort-template S] [--specific-name S]

    optional arguments:
      -h, --help            show this help message and exit
      --a-simple-option     🐢 (False, sets True)
      --main-jpeg-quality I 🐢 The jpeg quality level (int)
      --main-sync-dates-to… 🐢 (True, sets False)
      --main-work-in-place  🐢 (False, sets True)
      --rotate-resample S   🐢 (str)
      --sort-template S     🐢 (str)
      --specific-name S     🐢 (str)


Option help text can be set directly in the annotation with ``help='…'``.
To use a template for help based on a given description and auto-detected type,
use ``desc='…'`` instead.
The template is configurable as well via TurtleArgumentParser kwargs.

**Hiding Options:**

Options shown by an ArgumentParser can be hidden by passing the
``help=argparse.SUPPRESS``
value via the kwargs annotation to the option.

With enough options,
eventually the display of every possible option is too much,
and suppression gets tedious.
When something simpler to be presented to the end user is preferred,
this also works as you'd expect:

.. code-block:: python

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        '--quality', default=cfg['main.jpeg_quality'],
    )

Then, use ``args`` instead of ``cfg`` afterward for the options that take
precedence.
Remember—dots in an options string are presented as underscores in the
ArgumentParser Namespace,
and dashes on the command-line:

.. code-block:: python

    print('quality:', args.main_jpeg_quality)


Misc
---------

Performance
~~~~~~~~~~~~~~~

*"Why yes, it's a racing Turtle."*

The ``TurtleConfig`` object caches results so it doesn't have to go crawling
through multiple files to find the value every time.
So don't get fancy with changing the environment on the fly,
or editing config files unless you've cleared the cache with::

    cfg.clear_turtle_cache()


.. ~ After you're done with the ``TurtleConfig`` object,
.. ~ it can be deleted if needed to recycle the memory it's using.


Exceptions
~~~~~~~~~~~~~~~

These are thrown when a error occurs.

Access errors, say you've passed a bad name not found anywhere:

- ``AttributeError``,  *attribute interface*
- ``KeyError``,  *dict interface*

Option value errors, when the value returned is bogus:

- ``ValueError``,  *wrong value in this context*
- ``SyntaxError``,  *string unable to be evaluated*
- ``TypeError``,  *wrong type returned*


*Ob-la-di ob-la-da life goes on bra…*


License
~~~~~~~~~~~~~~~

Released under the LGPL, version 3+.


