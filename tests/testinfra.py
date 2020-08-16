""" This is a testinfra for ansible program."""


def test_passwd_file(host):
    """ Check passwd  """
    passwd = host.file("/etc/passwd")
    assert passwd.contains("root")
    assert passwd.user == "root"
    assert passwd.group == "root"
    assert passwd.mode == 0o644


def test_sshd_running_and_enabled(host):
    """ Check service sshd  """
    service = host.service("sshd")
    assert service.is_running
    assert service.is_enabled


def test_firewalld_running_and_enabled(host):
    """ Check service firewalld  """
    service = host.service("firewalld")
    assert service.is_running
    assert service.is_enabled


def test_openvipn_running_and_enabled(host):
    """ Check service openvpn  """
    service = host.service("vpnserver")
    assert service.is_running
    assert service.is_enabled


def test_hostname(host):
    """ Check hostname  """
    all_variables = host.ansible.get_variables()
    assert host.sysctl("kernel.hostname") == all_variables["hostname"]


def test_open_port(host):
    """ Check ports  """
    all_variables = host.ansible.get_variables()
    localhost = host.addr("localhost")
    # sshd
    assert localhost.port(all_variables["sshd_port"]).is_reachable
    if all_variables["sshd_port"] != 22:
        assert not localhost.port(22).is_reachable
    # vpnserver
    assert localhost.port(443).is_reachable
    assert localhost.port(5555).is_reachable
    assert localhost.port(1194).is_reachable


def test_ansible_user(host):
    """ Check exists ansible user  """
    all_variables = host.ansible.get_variables()
    for i in all_variables["ansible_users"].values():
        user = host.user(i["name"])
        assert user.exists
        assert user.name == i["name"]
        assert user.shell == i["login_shell"]
        assert user.home == "/home/" + i["name"]
