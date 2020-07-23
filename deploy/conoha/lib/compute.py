#!/usr/bin/env python
import json
import lib.token as t
from requests.exceptions import ConnectionError, RequestException, HTTPError
import requests
import sys
from time import sleep
from tqdm import tqdm

token_obj = t.Token()
config = token_obj.config
token = config["token"]["id"]
tenant = config["tenant"]


class example:
    def __init__(self):
        # with open('config.py', 'w') as f:
        #     json.dump(config, f, indent=4)
        #     # pickle.dump(str(config), f)

        with open("config.py", mode="w") as f:
            f.writelines(config)


class GetFlavorsDetails:
    def get_flavors():
        _api = "https://compute.tyo2.conoha.io/v2/" + tenant + "/flavors/detail"
        _header = {"Accept": "application/json", "X-Auth-Token": token}
        try:
            _res = requests.get(_api, headers=_header)
            if _res.status_code != 200:
                # return 'False', _res.status_code, ''
                return ""
            else:
                return json.loads(_res.text)["flavors"]

        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not get flavors detail.", e)
            sys.exit()


class SetFlavorDetail:
    def __init__(self):
        flavors = GetFlavorsDetails.get_flavors()
        for i in range(len(flavors[2])):
            print(
                "["
                + str(i)
                + "]"
                + "FlavorName:["
                + str(flavors[i]["name"])
                + "] ("
                + "Ram:"
                + str(flavors[i]["ram"])
                + "MB - "
                + "Disk:"
                + str(flavors[i]["disk"])
                + "GB)"
            )
        flavor_id = int(input("Enter Flavor number : "))
        token_obj.set_flavor_name(flavors[flavor_id])


class SetFlavorDetailParam:
    def __init__(self, flavor_name):
        flavors = GetFlavorsDetails.get_flavors()
        for i in range(len(flavors)):
            if flavors[i]["name"] == flavor_name:
                token_obj.set_flavor_name(flavors[i])
                break


class GetImagesDetail:
    def get_images():
        # if 'flavor' not in config:
        #     SetFlavorDetail()

        _api = "https://compute.tyo2.conoha.io/v2/" + tenant + "/images/detail"
        _header = {"Accept": "application/json", "X-Auth-Token": token}
        try:
            _res = requests.get(_api, headers=_header)
            if _res.status_code != 200:
                # return (False, _res.status_code, '')
                return ""
            else:
                return json.loads(_res.text)["images"]

        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not get flavor detail.", e)
            sys.exit()


class SetImageDetail:
    def __init__(self):
        images = GetImagesDetail.get_flavors()
        search_word = input(("Enter serch od keyword, centos-7.7, ubuntu , etc... : "))
        for i in range(len(images)):
            if str(search_word) in str(images[i]["name"]):
                print(
                    "["
                    + str(i)
                    + "]"
                    + "os:["
                    + str(images[i]["name"])
                    + "] ("
                    + "MinRam:"
                    + str(images[i]["minRam"])
                    + "MB - "
                    + "minDisk:"
                    + str(images[i]["minDisk"])
                    + "GB)"
                )
        #
        image_id = int(input("Enter image number : "))
        token_obj.set_image_name(images[image_id])


class SetImageDetailParam:
    def __init__(self, image_name):
        images = GetImagesDetail.get_images()
        for i in range(len(images)):
            if images[i]["name"] == image_name:
                token_obj.set_image_name(images[i])
                break


class GetServers:
    def __init__(self):
        if "flavor" not in config:
            SetFlavorDetail()

        _api = "https://compute.tyo2.conoha.io/v2/" + tenant + "/servers/detail"
        _header = {"Accept": "application/json", "X-Auth-Token": token}
        try:
            _res = requests.get(_api, headers=_header)
            if _res.status_code != 200:
                # print(_res.status_code)
                # print((json.loads(_res.text))(json.loads(_res.text)))
                return (True, _res.status_code, "")
            else:
                return (True, _res.status_code, (json.loads(_res.text)))

        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not get flavor detail.", e)
            sys.exit()


class AddVM:
    wait_time = 30  # sec

    def __init__(self):
        _api = "https://compute.tyo2.conoha.io/v2/" + tenant + "/servers"
        _header = {"Accept": "application/json", "X-Auth-Token": token}
        _body = {
            "server": {
                "adminPass": config["server_root_path"],
                "imageRef": config["image"]["id"],
                "flavorRef": config["flavor"]["id"],
                "metadata": {"instance_name_tag": config["tag_name"]},
            }
        }
        try:
            _res = requests.post(_api, data=json.dumps(_body), headers=_header)
            if _res.status_code != 202:
                print("Error Add VM")
            else:
                # print(_res.status_code)
                # print((json.loads(_res.text)))
                print("Please wait... " + str(self.wait_time) + "sec. Creating VM")
                for i in tqdm(range(self.wait_time)):
                    sleep(1)
                server = (json.loads(_res.text))["server"]
                server["detail"] = VmDetail.get_vm_detail(server["id"])
                token_obj.set_server(server)
            print("Success Add VM")

        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not Add VM.", e)
            sys.exit()


class VmDetail:
    @classmethod
    def get_vm_detail(cls, server_id):
        _api = "https://compute.tyo2.conoha.io/v2/" + tenant + "/servers/" + server_id
        _header = {"Accept": "application/json", "X-Auth-Token": token}
        try:
            _res = requests.get(_api, headers=_header)
            if _res.status_code != 200:
                print("Error get VM detail")
            else:
                return (json.loads(_res.text))["server"]

        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not get VM detail", e)
            sys.exit()

    @classmethod
    def get_vm_ipaddress(cls):
        break_loop = False
        for i in config["server"]["detail"]["addresses"]:
            for j in range(len(config["server"]["detail"]["addresses"][i])):
                # print(str(config['server']['detail']['addresses'][i][j]))
                if str(config["server"]["detail"]["addresses"][i][j]["version"]) == "4":
                    # print(config['server']['detail']['addresses'][i][j]['addr'])
                    print(config["server"]["detail"]["addresses"][i][j]["addr"])
                    break_loop = True
                    break
            if break_loop:
                break

    @classmethod
    def get_server_root_pass(cls):
        print(config["server"]["adminPass"])


class DestroyVM:
    def __init__(self):
        _api = (
            "https://compute.tyo2.conoha.io/v2/"
            + tenant
            + "/servers/"
            + config["server"]["id"]
        )
        _header = {"Accept": "application/json", "X-Auth-Token": token}
        try:
            _res = requests.delete(_api, headers=_header)
            if _res.status_code != 204:
                print("Error Destroy VM")
            else:
                print("Success Destroy VM")

        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not Destroy VM.", e)
            sys.exit()
