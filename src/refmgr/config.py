"""Config of refmgr."""

import configparser


def default():
    """Return the default config."""
    conf = configparser.ConfigParser()
    conf['library.path'] = '~/Documents/refmgr/'
    return conf


def config(path='~/.config/refmgr/conf'):
    """Returns the config after reading the config file at `path`."""
    conf = default()

    try:
        with open(path, 'r') as configfile:
            conf.read(configfile)
    except FileNotFoundError:
        # prevent errors if there is no config file
        pass

    return conf
