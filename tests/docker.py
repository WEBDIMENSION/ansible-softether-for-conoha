#!/usr/bin/env python
import os
import subprocess
from subprocess import PIPE
import yaml
import textwrap


# Init setting
docker_server = ""
docker_client = ""

marge_hosts = []
pwd = os.getcwd()


class DockerClass:
    vars_sshd = ""
    vars_ansible_user = ""
    vars_docker = ""
    server_ip = ""

    def __init__(self):
        global docker_server
        global docker_client
        global marge_hosts
        # Get ssh port from vas
        with open(pwd + "/group_vars/softether/sshd.yml", "r") as yml:
            self.vars_sshd = yaml.load(yml, Loader=yaml.SafeLoader)
        # Get master ansible user from vas
        with open(pwd + "/group_vars/softether/ansible_users.yml", "r") as yml:
            self.vars_ansible_user = yaml.load(yml, Loader=yaml.SafeLoader)
        # Get mount dir
        with open(pwd + "/group_vars/softether/docker.yml", "r") as yml:
            self.vars_docker = yaml.load(yml, Loader=yaml.SafeLoader)
            docker_server = self.vars_docker["docker_server"]
            docker_client = self.vars_docker["docker_client"]

        for i in range(len(docker_server["hosts"])):
            marge_hosts.append(docker_server["hosts"][i])
        for i in range(len(docker_client["hosts"])):
            marge_hosts.append(docker_client["hosts"][i])

    def cleanup_docker(self):
        # CleanUP Docker
        for i in range(len(marge_hosts)):
            try:
                subprocess.run(
                    "docker rm -f " + marge_hosts[i]["container_tag"],
                    shell=True,
                    check=True,
                )
            except subprocess.CalledProcessError:
                print("Not exists container " + marge_hosts[i]["container_tag"])

            try:
                subprocess.run(
                    "docker rmi  " + marge_hosts[i]["image_tag"],
                    shell=True,
                    check=True,
                )
            except subprocess.CalledProcessError:
                print("Not exists image " + marge_hosts[i]["image_tag"])

    def docker_run(self):
        for i in range(len(marge_hosts)):
            print("-- Dcoekr build ---")
            subprocess.run(
                "docker build . -t " + marge_hosts[i]["image_tag"],
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
                + str(marge_hosts[i]["ssh_port"])
                + ":22 --name "
                + marge_hosts[i]["container_tag"]
                + " "
                + marge_hosts[i]["image_tag"],
                shell=True,
                check=True,
            )

            # Get cotainer IP
            porcess = subprocess.run(
                'sudo docker inspect --format "{{ .NetworkSettings.IPAddress }}" '
                + marge_hosts[i]["container_tag"],
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                check=True,
            )
            self.container_ip = porcess.stdout
            marge_hosts[i]["container_ip"] = str(self.container_ip).strip()
            print(
                marge_hosts[i]["container_tag"]
                + " Container IP : "
                + str(self.container_ip)
            )

    def create_inventory(self):
        hosts_text = ""
        for i in range(len(docker_server["hosts"])):
            cname = str(docker_server["hosts"][i]["container_tag"])
            ip = str(docker_server["hosts"][i]["container_ip"])
            port = str(docker_server["hosts"][i]["ssh_port"])
            hosts_text += (
                str(cname + " ansible_host=" + ip + " ansile_port=" + port) + "\n"
            )
        SOFTETHER_INVENTORY_FILE = (
            textwrap.dedent(
                """\
        [softether]
        {hosts}
        [softether:vars]
        ansible_user=root
        ansible_ssh_pass=password
        """
            )
            .format(hosts=hosts_text)
            .strip()
        )

        hosts_text = ""
        for i in range(len(docker_server["hosts"])):
            cname = str(docker_server["hosts"][i]["container_tag"])
            ip = str(docker_server["hosts"][i]["container_ip"])
            port = str(docker_server["hosts"][i]["ssh_port"])
            hosts_text += str(cname + " ansible_host=" + ip) + "\n"
        os.makedirs(pwd + "/hosts", exist_ok=True)
        with open(
            pwd + "/hosts/" + docker_server["inventory_name"] + "_root", "w"
        ) as f:
            f.write(SOFTETHER_INVENTORY_FILE)
        SOFTETHER_INVENTORY_FILE = (
            textwrap.dedent(
                """\
        [softether]
        {hosts}
        [softether:vars]
        ansible_user={ansible_user}
        ansible_port={ansible_ssh_port}
        ansible_ssh_private_key_file={mount_dir}/roles/ansible_user/{key}\
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
        with open(
            pwd + "/hosts/" + docker_server["inventory_name"] + "_user", "w"
        ) as f:
            f.write(SOFTETHER_INVENTORY_FILE)

    def exec_tests(self):
        # pip install
        print("Start pip install ")
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
            + " && /root/.pyenv/shims/ansible-playbook site.yml -i hosts/"
            + docker_server["inventory_name"]
            + "_root"
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
            + " && /root/.pyenv/shims/ansible-playbook site.yml -i hosts/"
            + docker_server["inventory_name"]
            + "_user"
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
            + " --ansible-inventory='hosts/"
            + docker_server["inventory_name"]
            + "_user'\"",
            shell=True,
            check=True,
        )


obj = ""


def before_exec():
    print("before_exec: Start")
    global obj
    obj = DockerClass()
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
