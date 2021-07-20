# -*- coding: utf-8 -*-
import json
from configparser import ConfigParser

import requests

try:
    from wox import Wox as FlowLauncher
    from wox import WoxAPI as API
    PRETEXT = 'Wox'
except ModuleNotFoundError:
    from flowlauncher import FlowLauncher
    from flowlauncher import FlowLauncherAPI as API
    PRETEXT = 'Flow.Launcher'


CONFIG_FILE = './config.ini'

class Commander(FlowLauncher):

    def __init__(self):
        self.results = []
        self.load_config()
        if self.ssl:
            self.protocol = "http://"
        else:
            self.protocol = "https://"
        self.url = f"{self.protocol}{self.host}{self.port}/"
        self.get_states()
        super().__init__()

    def load_config(self):
        config = ConfigParser()
        config.read(CONFIG_FILE)
        _section = config.sections()[0]
        self.host = config[_section]['host']
        self.port = config[_section]['port']
        self.token = config[_section]['token']
        self.ssl = config[_section]['ssl']
        self.verify_ssl = config[_section]['verify_ssl']
        try:
        except:
            pass


    def context_menu(self, data):
        results = []
        results.append({
            "Title": "test",
            "SubTitle": "test",
            #"IcoPath":ico,
            "JsonRPCAction": {
                #change query to show only service type
                "method": "Wox.ChangeQuery",
                "parameters": ["ha" + " " + keywords, False],
                # hide the query wox or not
                "dontHideAfterAction": True
            }
        })
        return results

    def query(self, query):
                    "JsonRPCAction": {
                    }
                })



if __name__ == "__main__":
    Commander()
