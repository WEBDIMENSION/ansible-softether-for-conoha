#!/usr/bin/env python
import os
import subprocess
from subprocess import PIPE
import yaml

DEFAULT_SSH_PORT = 22
pwd = os.path.dirname(__file__)


class Deploy:
    """ Deploy to conoha server """

    def __init__(self):
        """ Create conoha config.json """
        # subprocess.run(pwd + "/commands.py make_config", shell=True)
        subprocess.run(pwd + "/commands.py make_config", shell=True, check=True)

    def before_deploy(self):
        """ before deploy script.  add server..."""
        self.add_vm()
        return self.deploy_ipaddress(), self.deploy_root_password()

    def after_deploy(self):
        """ after deploy script. destroy server... """
        self.destroy_vm()

    @classmethod
    def add_vm(cls):
        """ Add VM """
        subprocess.run(pwd + "/commands.py add_vm", shell=True, check=True)

    @classmethod
    def deploy_ipaddress(cls):
        """ get VM ipaddress """
        result = subprocess.run(
            pwd + "/commands.py get_vm_ip",
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            shell=True,
            check=True,
        )
        _server_ipaddress = result.stdout.strip()
        return _server_ipaddress

    def get_server_ipaddress(self):
        """ get VM ipaddress """
        print(self.deploy_ipaddress())
        print("success get ip")

    @classmethod
    def deploy_root_password(cls):
        """ get server root pass """
        result = subprocess.run(
            pwd + "/commands.py get_server_root_pass",
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            shell=True,
            check=True,
        )
        _server_root_password = result.stdout.strip()
        return _server_root_password

    def get_server_root_password(self):
        """ get server root pass """
        print(self.deploy_root_password())
        print("success server_root_pass")

    @classmethod
    def destroy_vm(cls):
        """ Add VM """
        subprocess.run(pwd + "/commands.py destroy_vm", shell=True, check=True)


def start_deploy():
    obj = Deploy()
    ret = obj.before_deploy()
    server_ipaddress = ret[0]
    server_root_password = ret[1]

    # pwd = os.path.dirname(__file__)
    crdir = os.getcwd()

    # Get ssh port from vas
    with open(crdir + "/group_vars/softether/sshd.yml", "r") as yml:
        vars_sshd = yaml.load(yml, Loader=yaml.SafeLoader)
    # Get master ansible user from vas
    with open(crdir + "/group_vars/softether/ansible_users.yml", "r") as yml:
        vars_ansible_user = yaml.load(yml, Loader=yaml.SafeLoader)

    # Write inventory file for Docker test
    INVENTORY_FILE = """\
    [softether]
    root
    ansible_user

    [add_ansible_user]
    root
    [add_ansible_user:vars]
    ansible_user=root
    ansible_host={server_ipaddress}
    ansible_port={default_ssh_port}
    ansible_ssh_pass={server_root_password}

    [ansible_users]
    ansible_user
    [ansible_users:vars]
    ansible_user={ansible_user}
    ansible_host={server_ipaddress}
    ansible_port={ansible_ssh_port}
    ansible_ssh_private_key_file={pwd}/roles/ansible-user/files/ansible_rsa
    """.format(
        server_ipaddress=server_ipaddress,
        default_ssh_port=DEFAULT_SSH_PORT,
        server_root_password=server_root_password,
        ansible_user=vars_ansible_user["ansible_users"]["master"]["name"],
        ansible_ssh_port=vars_sshd["sshd_port"],
        pwd=crdir,
    )

    os.makedirs(crdir + "/hosts", exist_ok=True)
    with open(crdir + "/hosts/product", "w") as f:
        f.write(INVENTORY_FILE)

    # Exec lint
    subprocess.run(
        "ansible-playbook -i hosts/product site.yml -l root  -t lint",
        shell=True,
        check=True,
    )

    # Exec Ansible
    subprocess.run(
        "ansible-playbook -i hosts/product site.yml -l root  -t softether",
        shell=True,
        check=True,
    )

    # Exec test
    subprocess.run(
        "py.test -v tests/testinfra.py\
        --connection=ssh\
        --hosts='ansible://ansible_user'\
        --ansible-inventory='hosts/product'",
        shell=True,
        stderr=subprocess.PIPE,
        check=True,
    )


obj = ""


def before_exec():
    print("before_exec: Start")
    global obj
    obj = Deploy()
    obj.cleanup_docker()
    obj.docker_run()
    obj.create_inventory()
    print("before_exec: End")


def exec():
    print("exec: Start")
    obj.exec_tests()
    print("exec: End")


def after_exec():
    print("after_exec: Start")
    obj.cleanup_docker()
    print("after_exec: End")
