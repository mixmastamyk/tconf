import sys
from os.path import dirname, join
from setuptools import setup
from tconf import meta


if sys.version_info < (3, 6):
    raise NotImplementedError('Sorry, only Python 3.6 and above is supported.')

# https://www.python.org/dev/peps/pep-0508/#environment-markers
install_requires = (
    'appdirs',
    'typeguard',
)
tests_require = ()  # ('pyflakes', 'readme_renderer'),
extras_require = dict(
    yaml=('strictyaml',),
    xml=('xmltodict',),
)

def slurp(filename):
    try:
        with open(join(dirname(__file__), filename), encoding='utf8') as infile:
            return infile.read()
    except FileNotFoundError:
        pass  # needed at upload time, not install time


setup(
    name                = meta.pkgname,
    description         = meta.description,
    author_email        = meta.email,
    author              = meta.authors,
    keywords            = meta.keywords,
    license             = meta.license,
    long_description    = slurp('readme.rst'),
    url                 = meta.repo_url,
    packages            = (meta.pkgname,),
    project_urls        = meta.project_urls,
    version             = meta.version,

    extras_require      = extras_require,
    install_requires    = install_requires,
    python_requires     = '>=3.6',
    setup_requires      = install_requires,
    tests_require       = tests_require,

    classifiers         = meta.trove_classifiers,
)
