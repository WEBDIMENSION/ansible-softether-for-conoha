#!/usr/bin/env python
""" This is a conoha API """
import datetime
import json
import os
from requests.exceptions import ConnectionError, RequestException, HTTPError
import requests

# import requests.exceptions
import sys

# CONFIG_DIR = "%s/.config/conoha/" % os.environ['HOME']
CONFIG_FILE = os.path.dirname(__file__) + "/../config.json"
# CONFIG_FILE_PATH = CONFIG_DIR + '/' + CONFIG_FILE
CONFIG_FILE_PATH = CONFIG_FILE


class Token:
    """ Active token class"""

    config = ""

    def __init__(self):
        if os.path.exists("%s" % (CONFIG_FILE_PATH)):
            config = json.load(open(CONFIG_FILE_PATH, "r"))
            if (
                datetime.datetime.strptime(
                    config["token"]["expires"], "%Y-%m-%dT%H:%M:%SZ"
                )
                <= datetime.datetime.now()
            ):
                token = self.create_conoha_token(
                    config["user"], config["password"], config["tenant"]
                )
                config["token"] = token[2]
                with open(CONFIG_FILE_PATH, "w") as _f:
                    json.dump(config, _f, indent=4)
        else:
            self.create_config()
        self.config = json.load(open(CONFIG_FILE_PATH, "r"))

    def create_config(self):
        """ Create config files """
        account_name = input("Enter  account name (free word) : ")
        user = input("Enter api user name : ")
        password = input("Enter api user password : ")
        tenant = input("Enter api tenant id : ")
        tag_name = input("Enter sever tag name (free word uniqe) : ")
        server_root_pass = input("Enter sever root password ( sec word) : ")
        token = self.create_conoha_token(user, password, tenant)
        if token[0]:
            _user = {}
            _user = {
                "user": user,
                "password": password,
                "tenant": tenant,
                "server_root_path": server_root_pass,
                "sec_group": "",
                "tag_name": tag_name,
                "script_path": "",
                "token": token[2],
            }
            _accounts = {}
            _accounts[account_name] = {
                "user": user,
                "password": password,
                "tenant": tenant,
                "server_root_path": server_root_pass,
                "sec_group": "",
                "tag_name": tag_name,
                "script_path": "",
                "token": token[2],
            }
            # os.makedirs(_c.CONFIG_DIR, exist_ok=True)
            with open("accounts.json", "a") as _f:
                json.dump(_accounts, _f, indent=4)
            with open(CONFIG_FILE_PATH, "w") as _f:
                json.dump(_user, _f, indent=4)
        else:
            print("Fiald get token. maybe missing user or password or tenant")
            self.create_config()

    @classmethod
    def create_conoha_token(cls, user, password, tenant):
        """ Create token   """
        _api = "https://identity.tyo2.conoha.io/v2.0/tokens"
        _header = {"Accept": "application/json"}
        _body = {
            "auth": {
                "passwordCredentials": {"username": user, "password": password},
                "tenantId": tenant,
            }
        }

        try:
            _res = requests.post(_api, data=json.dumps(_body), headers=_header)
            if _res.status_code != 200:
                return (False, _res.status_code, "")
            else:
                return (
                    True,
                    _res.status_code,
                    (json.loads(_res.text))["access"]["token"],
                )
        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as _e:
            print("Error: Could not Create token.", _e)
            sys.exit()

    @classmethod
    def set_flavor_name(cls, flavor):
        """ wirite flavor into config"""
        config = json.load(open(CONFIG_FILE_PATH, "r"))
        config["flavor"] = flavor
        with open(CONFIG_FILE_PATH, "w") as _f:
            json.dump(config, _f, indent=4)

    @classmethod
    def set_image_name(cls, image):
        """ wirite image into config"""
        config = json.load(open(CONFIG_FILE_PATH, "r"))
        config["image"] = image
        with open(CONFIG_FILE_PATH, "w") as _f:
            json.dump(config, _f, indent=4)

    @classmethod
    def set_server(cls, server):
        """ wirite serverinfo into config"""
        config = json.load(open(CONFIG_FILE_PATH, "r"))
        config["server"] = server
        with open(CONFIG_FILE_PATH, "w") as _f:
            json.dump(config, _f, indent=4)
