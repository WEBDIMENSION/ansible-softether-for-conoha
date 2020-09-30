# Conoha VPS サーバーでVPN (SoftEther) をAnsibleで構築

[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE) ![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/webdimension/ansible-softether-for-conoha?include_prereleases)

## 概要
Conoha VPNは立ち上げ時Rootでのログインのみとなる。
Rootログインのみの状況からVPN(SoftEther)を構築
- Conoha にてVPSサーバー立ち上げ
- AnsibleにてVPN構築
  - Rootでログイン
  - 一般ユーザー作成 ( ssh鍵登録 ）
  - sshd Root login を無効
  - パスワード認証無効  (鍵認証のみ)
  - Firewalld 設定
  - hostname 設定
  - SoftEther インストール

## 環境
***Local***
- Ubuntu 18.04
- Ansible 2.9.7
important consideration
***Server***
- CentOS 7.8 (Conoha VPS 512MB)

## 参考サイト
- <a href="https://galaxy.ansible.com/softasap/sa-vpn-softether" target="_blank">
  Ansible galaxy  [sa-vpn-softether]
  </a>
- <a href="https://github.com/softasap/sa-vpn-softether" target="_blank">
  Github [sa-vpn-softether]
  </a>

***改変箇所***
- AnsibleからSofteher Administrator password を設定できる。
  pipからInstallするpexpectでは意図するうごきならなかったため、
  shellモジュールでexpectを展開させた。

## 設定
### group_vars/softether/ansible_users.yml
``` yml
ansible_users:
  master:
    name: 'ansible' # username
    groups: 'wheel'
    append: 'yes'
    state: 'present'
    remove: 'no'
    password: "{{ secret.ansible_user_password }}"
    key: "files/ansible_rsa.pub"  # pulic_key 
    secret_key: "files/ansible_rsa" # secret_key
    login_shell: '/bin/bash'
    create_home: 'yes'
    sudo: 'present'
    comment: 'ansible user'
    expires: '-1'
# timezone
os_time_zone: "Asia/Tokyo"
```

### group_vars/softether/conoha.yml
``` yml
conoha_account:
  user: "user" # api user
  password: "pass" # api password
  tenant: "tenant_id" # api tenant_id
  sec_group: ""
  script_path: ""
conoha_servers:
  -  tag_name: "as_you_like001"
     server_root_password: "password"
     sec_group: ""
     script_path: ""
     flavor_name: "g-c1m512d30" # plan name
     image_name: "vmi-centos-7.8-amd64-30gb" # image name
  -  tag_name: "as_you_like002"
     server_root_password: "password"
     sec_group: ""
     script_path: ""
     flavor_name: "g-c1m512d30"
     image_name: "vmi-centos-7.8-amd64-30gb"
```
### group_vars/softether/docker.yml
```yml
mount_dir: '/softether'
project_name: 'Ansible-SoftEther'
docker_server:
  hosts:
    - host_ip: "127.0.0.1"
      ssh_port: 2223  # As you like
      image_tag: "softether"  # As you like
      container_tag: "softether001"  # As you like
      container_ip: ""
    - host_ip: "127.0.0.1"
      ssh_port: 2224  # As you like
      image_tag: "softether"  # As you likea
      container_tag: "softether002"  # As you like
      container_ip: ""
  image_tag: "softether"
  inventory_name: "docker_server"
docker_client:
  hosts:
    - host_ip: "127.0.0.1"
      ssh_port: 2222  # As you like
      image_tag: "softether_client"  # As you like
      container_tag: "softether_client"  # As you like
      container_ip: ""
  image_tag: "softether"  # As you like
  inventory_name: "docker_client" 
```
### group_vars/softether/hostname.yml
```yml
hostname: 'example.yourdomain' # as you like
```

### group_vars/conoha/sshs.yml
```yml
sshd_port: 50022 #Default 22
```

### group_vars/conoha/secret.yml
```yml
secret:
  ansible_user_password: 'User_Password'
  softether_ipsec_presharedkey: "Share_key"
  softether_administrator_password: 'SoftEther_Administrator_Password'
  softether_vpn_users: # SoftEther users
    - {
      name: "worker001",
      password: "workder001_password"
    }
    - {
      name: "worker002",
      password: "workder002_password"
    }
```

## Tests 実行
```bash
.tests.py
```
### 振る舞い
- Docker container 起動 (group_vars/softether/docker.yml)
- Inventoryfile 生成
- Dcoekr container (client) へ docker exec
  - ansile-lint
  - black
  - flake8
  - ansile-playbook
  - testinfra
- Docker cleanUp

## Diploy 実行
```bash
.deploy.py
```
### 振る舞い
- Docker container 起動 (group_vars/softether/docker.yml)
- Inventoryfile 生成
- conoha token生成
- conoha VPS生成
- Dcoekr container (client) へ docker exec
  - ansile-lint
  - black
  - flake8
  - ansile-playbook
  - testinfra

## クライアントツールのダウンロード

<a href="https://www.softether-download.com/en.aspx?product=softether" target="_blank">
Softether Download Center
</a>

### 機密情報の暗号化
### vault pass
```bash
echo 'vault_password_file = ./vaultpass' > ansible.cfg
cp valtpass.sample valtpass
echo 'your_vault_password' > vaultpass
```
#### 暗号化
```bash
ansible-vault encrypt group_vars/*/secret.yml 
```
#### 復号化
```bash
ansible-vault decrypt group_vars/*/secret.yml 
```

## License
MIT
