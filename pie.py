#!/usr/bin/env python

import argparse
import re
import os
from os.path import isfile
import subprocess
import sys

EXCLUDED_DIRS=['.hg', 'target', 'bin', 'classes']

# TODO: EXCLUDED_FILE_EXT=['.class', '.jar']

def listFiles(baseDir, searchstring, results=[]):
    dirList = os.listdir(baseDir)
    subDirs = []
    for item in dirList:
        path = os.path.join(baseDir, item)
        if isfile(path):
            if matches(searchstring, item):
                 # remove ./ at the beginning (can do with os.path?)
                results.append(path[2:])
        else:
            if item not in EXCLUDED_DIRS:
                subDirs.append(path)

    for subDir in subDirs:
        listFiles(subDir, searchstring, results)

    return results

def matches(searchstring, item):
    return re.search(searchstring, item, re.IGNORECASE)

def excludedDir(dir):
    excluded = dir in EXCLUDED_DIRS
    return excluded


""" Note: sub-process cannot change parent shell's CWD,
so the best we can do is just print the command for copy/pasting.
"""
def cd(path, **kwargs):
    print "cd", path[:path.rfind('/')]

def svn_diff(path, **kwargs):
    print "svn diff", path
    subprocess.call(["svn", "diff", path])

def hg_diff(path, **kwargs):
    print "hg diff", path
    subprocess.call(["hg", "diff", path])

def open_file(path, **kwargs):
    open_cmd = kwargs['editor']
    print open_cmd, path
    subprocess.call([open_cmd, path])

def execute(dir, searchstring, action, index, **kwargs):
    results = listFiles(os.curdir, searchstring)    
    if index is None and action is None:
        outputResults(results)
    else:
        checkIndex(index, results)
        if action is None: action = open_file
        executeAction(action, index, results, **kwargs)

def executeAction(action, index, results, **kwargs):
    for i, item in enumerate(results):
        if i == index: action(item, **kwargs)

def outputResults(results):
    for i, path in enumerate(results): print "%i: %s" % (i, path)

def checkIndex(index, results):
    if index < 0 or index > len(results) - 1:
        raise ValueError("There is no result number [%i]" % index)

def getIndex(args, action):
    if args.index is not None:
        return args.index
    elif action:
        return 0 # by default action on item 0
    return None # index won't be used

def getOpenCmd(args):
    if args.open is None:
        # default to EDITOR
        return os.environ.get('EDITOR')
    else:
        return args.open


def getAction(args):
    if args.cd:
        return cd
    elif args.svn_diff:
        return svn_diff
    elif args.hg_diff:
        return hg_diff
    elif args.open:
        return open_file
    return None


#eclipse --launcher.openFile <absolute path of file to open>

# TODO: symlinks seem to be broken

# find and print results
# ff file

# find and open file with [num]
# ff file [num]

# find and open file with [num] in [editor]
# ff file [num] --editor [editor]

# find and cd into directory to which the file belongs
# ff file [num] -cd

# find and do an svn diff
# ff file [num] --svn-diff

parser = argparse.ArgumentParser()
parser.add_argument('searchstring')
parser.add_argument('index', nargs='?', type=int)

group = parser.add_mutually_exclusive_group()
group.add_argument('--open', action='store')
group.add_argument('--cd', action='store_true')
group.add_argument('--svn-diff', action='store_true')
group.add_argument('--hg-diff', action='store_true')

args = parser.parse_args()
#print "=====================", args

action = getAction(args)
index = getIndex(args, action)
openCmd = getOpenCmd(args)
searchstring = args.searchstring


#print "exit"
#sys.exit()


#print 'searchstring =', searchstring
print 'action = ', action
#print 'index =', index
print 'openCmd =', openCmd #, openCmd.__class__.__name__




execute(os.curdir, searchstring, action, index, editor=openCmd)
