#!/usr/bin/env python
"""This is a conoha API """

import json
import lib.token as t
from requests.exceptions import ConnectionError, RequestException, HTTPError
import requests
import sys

token_obj = t.Token()
config = token_obj.config
token = config["token"]["id"]
tenant = config["tenant"]


class GetItems:
    def __init__(self):
        _api = "https://account.tyo2.conoha.io/v1/" + tenant + "/order-items"
        _header = {"Accept": "application/json", "X-Auth-Token": token}
        try:
            _res = requests.get(_api, headers=_header)
            if _res.status_code != 200:
                print(_res.status_code)
                print((json.loads(_res.text)))
            else:
                # print(_res.status_code)
                result = json.loads(_res.text)["order_items"]
                # print(result)
                for i in range(len(result)):
                    print(GetItemsDetail.GetItemsDetail(result[i]["uu_id"]))

        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not get items.", e)
            sys.exit()


class GetItemsDetail:
    @classmethod
    def GetItemsDetail(self, server_id):
        _api = (
            "https://account.tyo2.conoha.io/v1/" + tenant + "/order-items/" + server_id
        )
        _header = {"Accept": "application/json", "X-Auth-Token": token}
        try:
            _res = requests.get(_api, headers=_header)
            if _res.status_code != 200:
                print(_res.status_code)
                print((json.loads(_res.text)))
            else:
                return json.loads(_res.text)

        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not get items.", e)
            sys.exit()


class PaymentSummary:
    def __init__(self):
        _api = "https://account.tyo2.conoha.io/v1/" + tenant + "/payment-summary"
        _header = {"Accept": "application/json", "X-Auth-Token": token}
        try:
            _res = requests.get(_api, headers=_header)
            if _res.status_code != 200:
                print(_res.status_code)
                print((json.loads(_res.text)))
            else:
                print(_res.status_code)
                print((json.loads(_res.text)))
        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not get items.", e)
            sys.exit()


class PaymentHistory:
    def __init__(self):
        _api = "https://account.tyo2.conoha.io/v1/" + tenant + "/payment-history"
        _header = {"Accept": "application/json", "X-Auth-Token": token}
        try:
            _res = requests.get(_api, headers=_header)
            if _res.status_code != 200:
                print(_res.status_code)
                print((json.loads(_res.text)))
            else:
                print(_res.status_code)
                print((json.loads(_res.text)))

        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not get items.", e)
            sys.exit()
