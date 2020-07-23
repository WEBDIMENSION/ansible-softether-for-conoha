#!/usr/bin/env python
""" This is a conoha API """

import fire
import lib.account as account
import lib.make_config as conf
import lib.token as token
import lib.compute as compute


def make_config():
    """ make minimum config """
    conf.make_config()


#############################
# account
#############################


def load_token():
    """ active token """
    token.Token()


def example():
    """ For example """
    compute.example()


def set_flavor():
    """ Setting Flavor (plann) """
    compute.SetFlavorDetail()


def set_image():
    """ Setting image (os) """
    compute.SetImageDetail()


def get_servers():
    """ get active servers """
    compute.GetServers()


def add_vm():
    """ Add vm from config """
    compute.AddVM()


def get_vm_ip():
    """ Get IP address from create server """
    compute.VmDetail.get_vm_ipaddress()


def get_server_root_pass():
    """ Get Server root pass from create server """
    compute.VmDetail.get_server_root_pass()


def destroy_vm():
    """ Destory vm """
    compute.DestroyVM()


#############################
# account
#############################


def items():
    """ Get actinve servers """
    account.GetItems()


def payment_summary():
    """ Get payment information """
    account.PaymentSummary()


def payment_history():
    """ Get payment history """
    account.PaymentHistory()


if __name__ == "__main__":
    fire.Fire()
