# -*- coding: utf-8 -*-

DEFAULT_CONF = """
#
# $file is a placeholder for the selected file.
#
[KeyMappings]
e: EDITOR $file
d: git diff --color $file | less -R
l: less $file
g: gedit $file &

[Ignore]

# Ignore hidden files and directories.
ignore-hidden: true

# Ignore given directories
directories: bin, target

"""
