#!/usr/bin/env python
import json
import os
from requests.exceptions import ConnectionError, RequestException, HTTPError
import requests
import sys

default_config = {
    "user": "gncu27116007",
    "password": "9899Nori_7191",
    "tenant": "07dfade82c884c7d91dc133c7f068d8c",
    "server_root_path": "VV3bD1m3ns10n",
    "sec_group": "",
    "tag_name": "se_test",
    "script_path": "",
    "flavor_name": "g-c1m512d30",
    "image_name": "vmi-centos-7.8-amd64-30gb",
    "token": {"expires": "2000-01-01T00:00:00Z"},  # dummy
}

config_file_path = os.path.dirname(__file__) + "/../config.json"


class make_config:
    config = ""

    def __init__(self):
        self.config = default_config
        # import lib.token as t
        # ''' create token '''
        # self.token = t.Token()

    def create_config(self):
        pass

    def get_token(self):
        _api = "https://identity.tyo2.conoha.io/v2.0/tokens"
        _header = {"Accept": "application/json"}
        _body = {
            "auth": {
                "passwordCredentials": {
                    "username": self.config["user"],
                    "password": self.config["password"],
                },
                "tenantId": self.config["tenant"],
            }
        }
        try:
            _res = requests.post(_api, data=json.dumps(_body), headers=_header)
            if _res.status_code != 200:
                # return (False, _res.status_code, '')
                print("Erroe get token")
            else:
                self.config["token"] = json.loads(_res.text)["access"]["token"]

        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not Create token.", e)
            sys.exit()

    def get_flavor(self):
        _api = (
            "https://compute.tyo2.conoha.io/v2/"
            + self.config["tenant"]
            + "/flavors/detail"
        )
        _header = {
            "Accept": "application/json",
            "X-Auth-Token": self.config["token"]["id"],
        }
        try:
            _res = requests.get(_api, headers=_header)
            if _res.status_code != 200:
                print("Erroe get flavors")
            else:
                flavors = json.loads(_res.text)["flavors"]
                for i in range(len(flavors)):
                    if flavors[i]["name"] == self.config["flavor_name"]:
                        self.config["flavor"] = flavors[i]
                        break

        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not get flavors detail.", e)
            sys.exit()

    def get_image(self):
        _api = (
            "https://compute.tyo2.conoha.io/v2/"
            + self.config["tenant"]
            + "/images/detail"
        )
        _header = {
            "Accept": "application/json",
            "X-Auth-Token": self.config["token"]["id"],
        }
        try:
            _res = requests.get(_api, headers=_header)
            if _res.status_code != 200:
                print("Erroe get images")
            else:
                images = json.loads(_res.text)["images"]
                for i in range(len(images)):
                    if images[i]["name"] == self.config["image_name"]:
                        self.config["image"] = images[i]
                        break

        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not get images detail.", e)
            sys.exit()

    def write_config(self):
        with open(config_file_path, "w") as f:
            json.dump(self.config, f, indent=4)

    def exists_config(self):
        if os.path.exists(config_file_path):
            return True
        else:
            return False


# # def get_token():
# #     import lib.token as t
# #     ''' create token '''
# #     t.Token()
# #
# ''' Set flavor from dafault setting '''
# def set_flavor():
#     import lib.compute as c
#     c.SetFlavorDetailParam(default_config['flavor_name'])
#     import lib.token as t
#     ''' create token '''
#     # token = t.Token()
#     # print(token.config)
#
# # ''' Set image from dafault setting '''
# # def set_image():
# #    import lib.compute as c
# #    c.SetImageDetailParam(default_config['image_name'])
mk = make_config()
# print(config_file_path)
if not mk.exists_config():
    # print('not exist')
    mk.get_token()
    mk.get_flavor()
    mk.get_image()
    mk.write_config()
# get_token()
# mkset_flavor()
# set_image()
