# pie

`pie` is a very simple command-line utility for searching files.
It displays search results as a scrollable list and allows user-defined
commands to be run on a selected item.

## Usage

    pie searchstring [path]

This is equivalent to:

    find [path] -iname '*searchstring*' -type f

Example:

    pie log /var/log

## User-defined commands

`pie`'s config file will be created under user's home directory after
running `pie` for the first time.

    ~/.pie


This file can be customised with new keyboard shortcuts. For example,
to bind the key 'v' to `vim`, add the following line under `KeyMappings`.

    v: vim $file

This will allow opening selected files with `vim`.
