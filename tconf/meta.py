'''
    Project metadata is specified here.

    This module *should not* import anything from the project or third-party
    modules, to avoid dependencies in setup.py or circular import issues.
'''
from time import localtime as _localtime


pkgname         = 'tconf'
__version__     = version = '0.59a1'
__author__      = authors = ', '.join([
                                'Mike Miller',
                                #~ 'and contributors',
                            ])
copyright       = '© 2019-%s' % _localtime().tm_year
description     = "It's turtles all the way down…"
license         = 'LGPLv3'
keywords        = 'configuration cascade cascading ini conf yaml xml environment'

# online repo information
repo_account    = 'mixmastamyk'
repo_name       = pkgname
repo_provider   = 'github.com'
#~ repo_provider   = 'bitbucket.org'
repo_url        = 'https://%s/%s/%s' % (repo_provider, repo_account, repo_name)
project_urls    = {'Repository': repo_url, 'Issues': repo_url + '/issues'}
email           = 'mixmastamyk@%s' % repo_provider

trove_classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.6',
    'Topic :: System :: Systems Administration',
    'Topic :: Utilities',
]


class defaults:
    pass
