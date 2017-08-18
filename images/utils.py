"""Charlex utilities

This library is for useful utility functions that don't
belong anywhere else.

"""
__author__ = 'Michael Stella <mstella@charlex.com>'
__version__ = '$Id: utils.py 9423 2016-05-11 01:41:31Z psultan $'

import os
import sys
import shutil
import re
import unittest
from pprint import pprint
from collections import namedtuple
import chrlx
import glob
from enum import Enum
from functools import wraps

def getCurrentUser():
    """Cross-platform way to get the current user"""
    if (sys.platform == "win32"):
        import getpass
        return getpass.getuser()
    else:
        from pwd import getpwuid
        import os
        return getpwuid(os.getuid())[0]

def chown(path, uid, gid):
    if not os.name=="nt":
        os.chown(path, uid, gid)

def backupFile(fn, verbose=False):
    """Backs up a file into a directory called 'bak'
    If the backup file already exists, further files will be named
    .001, .002, etc.

    Optional argument 'verbose' will print to/from filenames.
    before moving.
    """
    if not os.path.exists(fn):
        raise IOError("file not found: " + fn)

    # create backup directory if it doesn't exist
    bkdir = os.path.join(os.path.dirname(fn), 'bak')
    if not os.path.isdir(bkdir):
        os.mkdir(bkdir)

    # new filename = oldpath/bak/filename
    newfn = os.path.join(bkdir, os.path.basename(fn))

    if os.path.exists(newfn):
        count = 1
        while (os.path.exists(newfn + '.%03d' % count)):
            count += 1;
        newfn = newfn + '.%03d' % count

    # move the file
    if verbose:
        print "moving %s -> %s" % (fn, newfn)
    os.rename(fn, newfn)

def orderedUniqueList(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]

def addEnv(key, values, index=0):
    if type(values)!=list:
        values=[values]
    values = [str(value) for value in values]
    values=orderedUniqueList(values)
    current=os.getenv(key)
    sep = ":" if os.name == "posix" else ";"

    if not current:
        os.environ[key]=sep.join(values)
        paths=values
    else:
        paths=current.split(sep)
        paths=orderedUniqueList(paths)
        for value in reversed(values):
            if value in paths:
                paths.remove(value)
            paths.insert(index,value)
        os.environ[key]=sep.join(paths)

    if key=="PYTHONPATH":
        for value in reversed(values):
            if value not in sys.path:
                sys.path.insert(index, value)

    return os.environ[key]

def copy_file(src, dst, overwrite):
    if not os.path.isfile(src):
        raise "can't copy '%s': doesn't exist or not a regular file" % src

    if os.path.exists(dst) and not overwrite:
        return dst, 0
    else:
        shutil.copy(src, dst)
        return (dst, 1)

def copy_tree(src, dst, overwrite=False):
    if not os.path.isdir(src):
        raise "cannot copy tree '%s': not a directory" % src

    try:
        names = os.listdir(src)
    except os.error, (errno, errstr):
        raise "error listing files in '%s': %s" % (src, errstr)

    if not os.path.exists(dst):
        os.makedirs(dst)

    outputs = []
    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)

        if os.path.isdir(src_name):
            outputs.extend(copy_tree(src_name, dst_name, overwrite))
        else:
            copy_file(src_name, dst_name, overwrite)
            outputs.append(dst_name)

    return

def head(f, lines=20):
    if type(f)==str:
        if os.path.exists(f):
            f=open(f)

    return [next(f) for x in range(lines)]

def tail( f, lines=20 ):
    '''tail a file'''
    if type(f)==str:
        if os.path.exists(f):
            f=open(f)

    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = [] # blocks of size BLOCK_SIZE, in reverse order starting
                # from the end of the file
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            # read the last block we haven't yet read
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count('\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = ''.join(reversed(blocks))
    return all_read_text.splitlines()[-total_lines_wanted:]

def uid2Email(uid):
    try:
        import ldap_utils
        return ldap_utils.uid2Email(uid)
    except:
        return '{0}@charlex.com'.format(uid)

if __name__ == "__main__":
    pass
