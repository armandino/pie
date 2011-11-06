import ConfigParser
import os

class PieConfig:
    CONFIG_FILE = '~/.pie'

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.expanduser(self.CONFIG_FILE))

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

