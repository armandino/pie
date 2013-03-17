# -*- coding: utf-8 -*-
import ConfigParser
import os
from defaultconf import *

_USER_HOME_CONF_FILE = os.path.join(os.getenv('HOME'), '.pie')

class PieConfig:

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.expanduser(self.get_conf_path()))

    def get_conf_path(args):
        if not os.path.isfile(_USER_HOME_CONF_FILE):
            with open(_USER_HOME_CONF_FILE, 'w+') as f:
                f.write(DEFAULT_CONF)
        return _USER_HOME_CONF_FILE

    def get_key_command_mappings(self):
        action_map = {}
        try:
            actions = self.config.items('KeyMappings')
            for action in actions:
                action_name = action[0]
                action_cmd = action[1]
                action_map[action_name] = action_cmd
        except:
            pass
        return action_map

    def get_ignored_dirs(self):
        ignored = []
        try:
            value = self.config.get('Ignore', 'directories')
            ignored = [x.strip() for x in value.split(',')]
        except:
            pass
        return ignored

    def ignore_hidden(self):
        try:
            return self.config.getboolean('Ignore', 'ignore-hidden')
        except:
            pass
        return False
        
