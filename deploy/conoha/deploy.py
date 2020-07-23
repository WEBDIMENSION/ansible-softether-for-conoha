#!/usr/bin/env python
import os
import subprocess
from requests.exceptions import ConnectionError, RequestException, HTTPError
import requests
import yaml
import textwrap
import json
import sys
from time import sleep
from tqdm import tqdm
import datetime

DEFAULT_SSH_PORT = 22
# pwd = os.path.dirname(__file__)
pwd = os.getcwd()

docker_client = ""
conoha_servers = ""
CONFIG_DIR = pwd + "/deploy/conoha/config"
token = ""


class DeployClass:
    vars_sshd = ""
    vars_ansible_user = ""
    vars_docker = ""
    vars_conoha = ""
    """ Deploy to conoha server """

    def __init__(self):
        global docker_client
        global conoha_servers
        global token
        # Get ssh port from vas
        with open(pwd + "/group_vars/softether/sshd.yml", "r") as yml:
            self.vars_sshd = yaml.load(yml, Loader=yaml.SafeLoader)
        # Get master ansible user from vas
        with open(pwd + "/group_vars/softether/ansible_users.yml", "r") as yml:
            self.vars_ansible_user = yaml.load(yml, Loader=yaml.SafeLoader)
        # Get mount dir
        with open(pwd + "/group_vars/softether/docker.yml", "r") as yml:
            self.vars_docker = yaml.load(yml, Loader=yaml.SafeLoader)
            docker_client = self.vars_docker["docker_client"]
        # set conoha awccount
        with open(pwd + "/group_vars/softether/conoha.yml", "r") as yml:
            self.vars_conoha = yaml.load(yml, Loader=yaml.SafeLoader)
            conoha_servers = self.vars_conoha["conoha_servers"]

        # Set Tolen
        if not os.path.exists(CONFIG_DIR + "token.json"):
            _token = self.create_token()
            with open(CONFIG_DIR + "/token.json", "w") as _f:
                json.dump(_token[2], _f, indent=4)
        else:
            _token = json.load(open(CONFIG_DIR + "/token.json", "r"))
            if (
                datetime.datetime.strptime(
                    token["token"]["expires"], "%Y-%m-%dT%H:%M:%SZ"
                )
                <= datetime.datetime.now()
            ):
                token = self.create_token()
                with open(CONFIG_DIR + "/token.json", "w") as _f:
                    json.dump(_token[2], _f, indent=4)

        token = json.load(open(CONFIG_DIR + "/token.json", "r"))

    def create_token(self):
        _api = "https://identity.tyo2.conoha.io/v2.0/tokens"
        _header = {"Accept": "application/json"}
        _body = {
            "auth": {
                "passwordCredentials": {
                    "username": self.vars_conoha["conoha_account"]["user"],
                    "password": self.vars_conoha["conoha_account"]["password"],
                },
                "tenantId": self.vars_conoha["conoha_account"]["tenant"],
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

    def add_vm(self):
        servers = []
        wait_time = 30
        for i in range(len(conoha_servers)):

            flavor_detail = self.get_flavor_detail(conoha_servers[i]["flavor_name"])
            with open(
                CONFIG_DIR + "/" + conoha_servers[i]["tag_name"] + "_flavor.json", "w"
            ) as _f:
                json.dump(flavor_detail, _f, indent=4)

            image_detail = self.get_image_detail(conoha_servers[i]["image_name"])
            with open(
                CONFIG_DIR + "/" + conoha_servers[i]["tag_name"] + "_image.json", "w"
            ) as _f:
                json.dump(image_detail, _f, indent=4)

            _api = (
                "https://compute.tyo2.conoha.io/v2/"
                + token["tenant"]["id"]
                + "/servers"
            )
            _header = {"Accept": "application/json", "X-Auth-Token": token["id"]}
            _body = {
                "server": {
                    "adminPass": conoha_servers[i]["server_root_password"],
                    "imageRef": image_detail["id"],
                    "flavorRef": flavor_detail["id"],
                    "metadata": {"instance_name_tag": conoha_servers[i]["tag_name"]},
                }
            }
            try:
                _res = requests.post(_api, data=json.dumps(_body), headers=_header)
                if _res.status_code != 202:
                    print(_res.status_code)
                    print(_api)
                    print(_header)
                    print(_body)
                    print(_res.text)
                    print("Error Add VM")
                else:
                    print("Please wait... " + str(wait_time) + "sec. Creating VM")

                    for t in tqdm(range(wait_time)):
                        sleep(1)

                    server = (json.loads(_res.text))["server"]
                    server["flavor"] = flavor_detail
                    server["image"] = image_detail
                    server["detail"] = self.get_vm_detail(server["id"])
                    with open(
                        CONFIG_DIR
                        + "/"
                        + conoha_servers[i]["tag_name"]
                        + "_server.json",
                        "w",
                    ) as _f:
                        json.dump(server, _f, indent=4)

                    servers.append(server)

            except (
                ValueError,
                NameError,
                ConnectionError,
                RequestException,
                HTTPError,
            ) as e:
                print("Error: Could not Add VM.", e)
                sys.exit()
        with open(CONFIG_DIR + "/" + "servers.json", "w",) as _f:
            json.dump(servers, _f, indent=4)
        print("Success Add VM")

    def get_flavor_detail(self, flavor_name):
        _api = (
            "https://compute.tyo2.conoha.io/v2/"
            + token["tenant"]["id"]
            + "/flavors/detail"
        )
        _header = {"Accept": "application/json", "X-Auth-Token": token["id"]}
        try:
            _res = requests.get(_api, headers=_header)
            if _res.status_code != 200:
                print("Error: can not get flavor detail")
            else:
                flavors = json.loads(_res.text)["flavors"]
        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not get flavors detail.", e)
            sys.exit()

        for i in range(len(flavors)):
            if flavors[i]["name"] == flavor_name:
                return flavors[i]
                break

    def get_image_detail(self, image_name):
        _api = (
            "https://compute.tyo2.conoha.io/v2/"
            + token["tenant"]["id"]
            + "/images/detail"
        )
        _header = {"Accept": "application/json", "X-Auth-Token": token["id"]}
        try:
            _res = requests.get(_api, headers=_header)
            if _res.status_code != 200:
                print("Error: can not get image detail")
            else:
                images = json.loads(_res.text)["images"]
        except (
            ValueError,
            NameError,
            ConnectionError,
            RequestException,
            HTTPError,
        ) as e:
            print("Error: Could not get image detail.", e)
            sys.exit()

        for i in range(len(images)):
            if images[i]["name"] == image_name:
                return images[i]
                break

    def get_vm_detail(self, server_id):
        _api = (
            "https://compute.tyo2.conoha.io/v2/"
            + token["tenant"]["id"]
            + "/servers/"
            + server_id
        )
        _header = {"Accept": "application/json", "X-Auth-Token": token["id"]}
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

    def cleanup_docker(self):
        # CleanUP Docker
        for i in range(len(docker_client["hosts"])):
            try:
                subprocess.run(
                    "docker rm -f " + docker_client["hosts"][i]["container_tag"],
                    shell=True,
                    check=True,
                )
            except subprocess.CalledProcessError:
                print(
                    "Not exists container " + docker_client["hosts"][i]["container_tag"]
                )

            try:
                subprocess.run(
                    "docker rmi  " + docker_client["hosts"][i]["image_tag"],
                    shell=True,
                    check=True,
                )
            except subprocess.CalledProcessError:
                print("Not exists image " + docker_client["hosts"][i]["image_tag"])

    def docker_run(self):
        for i in range(len(docker_client["hosts"])):
            print("-- Dcoekr build ---")
            subprocess.run(
                "docker build . -t " + docker_client["hosts"][i]["image_tag"],
                shell=True,
                check=True,
            )
            # project_name = self.vars_docker["project_name"]
            print("--- Dcoekr run ---")
            subprocess.run(
                "docker run -itd --privileged -v "
                + pwd
                + "/../"
                + self.vars_docker["project_name"]
                + ":"
                + self.vars_docker["mount_dir"]
                + " -p "
                + str(docker_client["hosts"][i]["ssh_port"])
                + ":22 --name "
                + docker_client["hosts"][i]["container_tag"]
                + " "
                + docker_client["hosts"][i]["image_tag"],
                shell=True,
                check=True,
            )

    def create_inventory(self):
        servers = json.load(open(CONFIG_DIR + "/servers.json", "r"))
        hosts_text = ""
        for i in range(len(servers)):
            cname = str(servers[i]["detail"]["metadata"]["instance_name_tag"])
            ip = str(self.get_vm_ipaddress(servers[i]["detail"]["addresses"]))
            port = str(22)
            admin_password = servers[i]["adminPass"]
            hosts_text += (
                str(
                    cname
                    + " ansible_host="
                    + ip
                    + " ansible_port="
                    + port
                    + " ansible_password="
                    + admin_password
                )
                + "\n"
            )
        SOFTETHER_INVENTORY_FILE = (
            textwrap.dedent(
                """\
        [softether]
        {hosts}
        [softether:vars]
        ansible_user=root
        """
            )
            .format(hosts=hosts_text)
            .strip()
        )
        os.makedirs(pwd + "/hosts", exist_ok=True)
        with open(pwd + "/hosts/product" + "_root", "w") as f:
            f.write(SOFTETHER_INVENTORY_FILE)

        hosts_text = ""
        for i in range(len(servers)):
            cname = str(servers[i]["detail"]["metadata"]["instance_name_tag"])
            ip = str(self.get_vm_ipaddress(servers[i]["detail"]["addresses"]))
            hosts_text += str(cname + " ansible_host=" + ip) + "\n"
        SOFTETHER_INVENTORY_FILE = (
            textwrap.dedent(
                """\
        [softether]
        {hosts}
        [softether:vars]
        ansible_user={ansible_user}
        ansible_port={ansible_ssh_port}
        ansible_ssh_private_key_file={mount_dir}/roles/ansible-user/{key}\
        """
            )
            .format(
                hosts=hosts_text,
                ansible_user=self.vars_ansible_user["ansible_users"]["master"]["name"],
                ansible_ssh_port=self.vars_sshd["sshd_port"],
                mount_dir=self.vars_docker["mount_dir"],
                key=self.vars_ansible_user["ansible_users"]["master"]["secret_key"],
            )
            .strip()
        )
        os.makedirs(pwd + "/hosts", exist_ok=True)
        with open(pwd + "/hosts/product" + "_user", "w") as f:
            f.write(SOFTETHER_INVENTORY_FILE)

    def get_vm_ipaddress(self, addresses):
        break_loop = False
        for i in addresses:
            for j in range(len(addresses[i])):
                if str(addresses[i][j]["version"]) == "4":
                    ipaddress = addresses[i][j]["addr"]
                    break_loop = True
                    break
            if break_loop:
                break
        return ipaddress

    def exec_deploy(self):
        # ansible-int
        subprocess.run(
            "docker exec -it "
            + docker_client["hosts"][0]["container_tag"]
            + " bash -c 'cd "
            + str(self.vars_docker["mount_dir"])
            + " && /root/.pyenv/shims/pip install -r requirements.txt'",
            shell=True,
            check=True,
        )
        # pip upgrade
        print("Start pip upgrade ")
        subprocess.run(
            "docker exec -it "
            + docker_client["hosts"][0]["container_tag"]
            + " bash -c 'cd "
            + str(self.vars_docker["mount_dir"])
            + " && /root/.pyenv/shims/pip install --upgrade pip'",
            shell=True,
            check=True,
        )
        # ansible-int
        print("Start ansible-lint")
        subprocess.run(
            "docker exec -it "
            + docker_client["hosts"][0]["container_tag"]
            + " bash -c 'cd "
            + str(self.vars_docker["mount_dir"])
            + " && /root/.pyenv/shims/ansible-lint site.yml'",
            shell=True,
            check=True,
        )

        # Exec black
        print("Start black")
        subprocess.run(
            "docker exec -it "
            + docker_client["hosts"][0]["container_tag"]
            + " bash -c 'cd "
            + str(self.vars_docker["mount_dir"])
            + " && /root/.pyenv/shims/black tests tests.py deploy deploy.py'",
            shell=True,
            check=True,
        )
        # Exec flake8
        print("Start flake8")
        subprocess.run(
            "docker exec -it "
            + docker_client["hosts"][0]["container_tag"]
            + " bash -c 'cd "
            + str(self.vars_docker["mount_dir"])
            + " && /root/.pyenv/shims/flake8 tests tests.py deploy deploy.py'",
            shell=True,
            check=True,
        )
        # exec softether
        subprocess.run(
            "docker exec -it "
            + docker_client["hosts"][0]["container_tag"]
            + " bash -c 'cd "
            + str(self.vars_docker["mount_dir"])
            + " && /root/.pyenv/shims/ansible-playbook site.yml -i hosts/product_root"
            + " -t softether'",
            shell=True,
            check=True,
        )
        # exec tools
        subprocess.run(
            "docker exec -it "
            + docker_client["hosts"][0]["container_tag"]
            + " bash -c 'cd "
            + str(self.vars_docker["mount_dir"])
            + " && /root/.pyenv/shims/ansible-playbook site.yml -i hosts/product_user"
            + " -t tools'",
            shell=True,
            check=True,
        )
        # exec testinfra
        print("Start testinfra")
        subprocess.run(
            "docker exec -it "
            + docker_client["hosts"][0]["container_tag"]
            + ' bash -c "cd '
            + str(self.vars_docker["mount_dir"])
            + " && /root/.pyenv/shims/py.test -v tests/testinfra.py"
            + " --connection=ssh"
            + " --hosts='ansible://softether'"
            + " --ansible-inventory='hosts/product_user'\"",
            shell=True,
            check=True,
        )


obj = ""


def before_exec():
    print("before_exec: Start")
    global obj
    obj = DeployClass()
    obj.cleanup_docker()
    obj.docker_run()
    obj.add_vm()
    obj.create_inventory()
    print("before_exec: End")


def exec():
    print("exec: Start")
    obj.exec_deploy()
    print("exec: End")


def after_exec():
    print("after_exec: Start")
    obj.cleanup_docker()
    print("after_exec: End")

    # def before_deploy(self):
    #     """ before deploy script.  add server..."""
    #     self.add_vm()
    #     return self.deploy_ipaddress(), self.deploy_root_password()

    # def after_deploy(self):
    #     """ after deploy script. destroy server... """
    #     self.destroy_vm()

    # # @classmethod
    # def deploy_ipaddress(cls):
    #     """ get VM ipaddress """
    #     result = subprocess.run(
    #         pwd + "/commands.py get_vm_ip",
    #         stdout=PIPE,
    #         stderr=PIPE,
    #         text=True,
    #         shell=True,
    #         check=True,
    #     )
    #     _server_ipaddress = result.stdout.strip()
    #     return _server_ipaddress

    # def get_server_ipaddress(self):
    #     """ get VM ipaddress """
    #     print(self.deploy_ipaddress())
    #     print("success get ip")

    # # @classmethod
    # def deploy_root_password(cls):
    #     """ get server root pass """
    #     result = subprocess.run(
    #         pwd + "/commands.py get_server_root_pass",
    #         stdout=PIPE,
    #         stderr=PIPE,
    #         text=True,
    #         shell=True,
    #         check=True,
    #     )
    #     _server_root_password = result.stdout.strip()
    #     return _server_root_password

    # def get_server_root_password(self):
    #     """ get server root pass """
    #     print(self.deploy_root_password())
    #     print("success server_root_pass")

    # # @classmethod
    # def destroy_vm(cls):
    #     """ Add VM """
    #     subprocess.run(pwd + "/commands.py destroy_vm", shell=True, check=True)

    # def exec():
    #     obj = Deploy()
    #     ret = obj.before_deploy()
    #     server_ipaddress = ret[0]
    #     server_root_password = ret[1]

    #     # pwd = os.path.dirname(__file__)
    #     crdir = os.getcwd()

    #     # Get ssh port from vas
    #     with open(crdir + "/group_vars/softether/sshd.yml", "r") as yml:
    #         vars_sshd = yaml.load(yml, Loader=yaml.SafeLoader)
    #     # Get master ansible user from vas
    #     with open(crdir + "/group_vars/softether/ansible_users.yml", "r") as yml:
    #         vars_ansible_user = yaml.load(yml, Loader=yaml.SafeLoader)

    #     # Write inventory file for Docker test
    #     INVENTORY_FILE = """\
    #     [softether]
    #     root
    #     ansible_user

    #     [add_ansible_user]
    #     root
    #     [add_ansible_user:vars]
    #     ansible_user=root
    #     ansible_host={server_ipaddress}
    #     ansible_port={default_ssh_port}
    #     ansible_ssh_pass={server_root_password}

    #     [ansible_users]
    #     ansible_user
    #     [ansible_users:vars]
    #     ansible_user={ansible_user}
    #     ansible_host={server_ipaddress}
    #     ansible_port={ansible_ssh_port}
    #     ansible_ssh_private_key_file={pwd}/roles/ansible-user/files/ansible_rsa
    #     """.format(
    #         server_ipaddress=server_ipaddress,
    #         default_ssh_port=DEFAULT_SSH_PORT,
    #         server_root_password=server_root_password,
    #         ansible_user=vars_ansible_user["ansible_users"]["master"]["name"],
    #         ansible_ssh_port=vars_sshd["sshd_port"],
    #         pwd=crdir,
    #     )

    #     os.makedirs(crdir + "/hosts", exist_ok=True)
    #     with open(crdir + "/hosts/product", "w") as f:
    #         f.write(INVENTORY_FILE)

    #     # Exec lint
    #     subprocess.run(
    #         "ansible-playbook -i hosts/product site.yml -l root  -t lint",
    #         shell=True,
    #         check=True,
    #     )

    #     # Exec Ansible
    #     subprocess.run(
    #         "ansible-playbook -i hosts/product site.yml -l root  -t softether",
    #         shell=True,
    #         check=True,
    #     )

    #     # Exec test
    #     subprocess.run(
    #         "py.test -v tests/testinfra.py\
    #         --connection=ssh\
    #         --hosts='ansible://ansible_user'\
    #         --ansible-inventory='hosts/product'",
    #         shell=True,
    #         stderr=subprocess.PIPE,
    #         check=True,
    #     )
