#! /usr/bin/env python3
__version__ = '0.0.1'
import os
import argparse
import netifaces
import socket
import configparser
from random import randint
from subprocess import check_output
#from .index import get_pass, generate_pass

# always ignore compiled files, .git dirs, as well as backup and temporary files.
ALWAYS_IGNORE = ['*.pyc', '~*', '*.tmp', '*.bak', '.goutputstream-*', '*.swp', '*.bin']
RESERVED_NAMES = ['root', 'admin', 'origin', 'git', 'master', 'localhost', 'gitolite-admin', 'cdrom', 'wheel', 'audio', 'video', 'adm', 'sambashare', 'sudo', 'www-data', 'http', 'lpadmin', 'plugdev', 'dip']

try:
    GEN_PASS_LEN = os.environ['GEN_PASS_LEN']
except KeyError:
    # is this pseudo-randomized length actually helping?
    GEN_PASS_LEN = 25 + randint(-5, 5)

try:
    BLOCKTREE = os.environ['BLOCKTREE']
except KeyError:
    BLOCKTREE = "/BLOCKTREE"

def mkdirp(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == os.errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class GuldConfig(object):
    def __init__(self):
        self._hostname = None
        self._interface = None
        self._git_config = None
        self._admin = None

    @property
    def hostname(self):
        if self._hostname is None:
            self._hostname = socket.gethostname()
        return self._hostname

    @property
    def interfaces(self):
        if self._interface is None:
            self._interface = netifaces.interfaces()
            self._interface.remove('lo')
        return self._interface

    @property
    def devicename(self):
        if self._devicename is None:
            self._devicename, self._admin = self.hostname.split('.')
        return self._devicename

    @property
    def admin(self):
        if self._admin is None:
            self._devicename, self._admin = self.hostname.split('.')
        return self._admin

    @property
    def git_config(self, user=None):
        if user is None:
            user = self.admin
        if self._git_config is None:
            self._git_config = configparser.ConfigParser()
            self._git_config.read_file(open(os.path.join(BLOCKTREE, self.admin, '.gitconfig')))
        return self._git_config

    @property
    def name(self):
        return self.git_config.get('user', 'name')

    @name.setter
    def name(self, user):
        self._name = user
        self.git_config.set('user', 'name', user)
        with open(os.path.join(BLOCKTREE, self.username, '.gitconfig'), 'r+') as f:
            self.git_config.write(f)

    @property
    def username(self):
        return self.git_config.get('user', 'username')

    @username.setter
    def username(self, user):
        self._username = user
        self.git_config.set('user', 'username', user)
        with open(os.path.join(BLOCKTREE, self.username, '.gitconfig'), 'r+') as f:
            self.git_config.write(f)

    @property
    def email(self):
        return self.git_config.get('user', 'email')

    @email.setter
    def email(self, email):
        self._email = email
        self.git_config.set('user', 'email', email)
        with open(os.path.join(BLOCKTREE, self.username, '.gitconfig'), 'r+') as f:
            self.git_config.write(f)

    @property
    def signingkey(self):
        return self.git_config.get('user', 'signingkey')

    @signingkey.setter
    def signingkey(self, signingkey):
        self._signingkey = signingkey
        self.git_config.set('user', 'signingkey', signingkey)
        with open(os.path.join(BLOCKTREE, self.username, '.gitconfig'), 'r+') as f:
            self.git_config.write(f)

    @property
    def sign(self):
        return self.git_config.get('commit', 'gpgsign') == 'true'

    @sign.setter
    def sign(self, sign=True):
        # sign is ignored, since there is only one valid value
        # call once per installation
        self.git_config.set('commit', 'gpgsign', 'true')
        with open(os.path.join(BLOCKTREE, self.username, '.gitconfig'), 'r+') as f:
            self.git_config.write(f)

    @classmethod
    def rawpath(cls, path, user):
        if (path.startswith(BLOCKTREE)):
            raise FuseOSError(os.errno.ENOENT)
        elif (not path.startswith(BLOCKTREE) and path.startswith('/home')):
            return path.replace('/home', BLOCKTREE)
        else:
            return os.path.join(BLOCKTREE, path.strip('/'))

    @classmethod
    def mountpath(cls, path, user):
        if path.startswith(BLOCKTREE):
            return path.replace(BLOCKTREE, '')
        elif path.startswith('/home'):
            return path.replace('/home', '')
        else:
            return path

    def __dict__(self):
        return {
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "signingkey": self.signingkey,
            "sign": self.sign,
            "devicename": self.devicename,
            "hostname": self.hostname
        }

def main():
    parser = argparse.ArgumentParser('guld-config')
    parser.add_argument("key", nargs="*", help="Get or set (second position) name, username, email, signingkey, sign.")#, choices=["name", "username", "email", "signingkey", "sign-commits"])
    args = parser.parse_args()
    cfg = GuldConfig()
    if args.key and len(args.key) == 1:
        print(getattr(cfg, args.key[0]))
    elif args.key and len(args.key) == 2:
        setattr(cfg, args.key[0], args.key[1])
        print("set %s" % args.key[0])
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

