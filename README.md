# Conoha VPS サーバーでVPN (SoftEther) をAnsibleで構築

![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/webdimension/ansible-softether-for-conoha?include_prereleases)

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
- python 3.7.6
- Docker version 19.03.12

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
### group_vars/conoha/common.yml
```yml
ansible_users:
  master:
    name: 'ansible'  # Ansible user name
    groups: 'wheel'
    append: 'yes'
    state: 'present'
    remove: 'no'
    password: "{{ secret.ansible_user_password }}"
    key: "files/ansible_rsa.pub"  # ssh public_key
    secret_key: "files/ansible_rsa" # ssh private_key
    login_shell: '/bin/bash'
    create_home: 'yes'
    sudo: 'present'
    comment: 'ansible user'
    expires: '-1'
```
### group_vars/conoha/docker.yml
```yml
mount_dir: '/softether' # contaiter mount dir (docer -v ..)
project_name: 'Ansible-SoftEther' # this project dir name
docker_server:  # For test
  hosts:  # Test hosts
    - host_ip: "127.0.0.1"
      ssh_port: 2223  # this is example, change your environment
      image_tag: "softether" # As you like
      container_tag: "softether001" # As you like
      container_ip: ""
    - host_ip: "127.0.0.1"
      ssh_port: 2224 # this is example, change your environment
      image_tag: "softether" # As you like
      container_tag: "softether002" # As you like
      container_ip: ""
  image_tag: "softether" # As you like
  inventory_name: "docker_server"  # As you like
docker_client:  # For test and doploy
  hosts:
    - host_ip: "127.0.0.1"
      ssh_port: 2222  # this is example, change your environment
      image_tag: "softether_client" # As you like
      container_tag: "softether_client" # As you like
      container_ip: ""
  image_tag: "softether" # As you like
  inventory_name: "docker_client" # As you like


```
### group_vars/conoha/uers.yml
```yml
users: #users
  - name: 'user_name' # username
    groups: 'wheel'
    append: 'yes'
    state: 'present'
    remove: 'no'
    password: "{{ secret.ansible_user_password }}"
    key: "~/.ssh/ansible_rsa.pub"  #公開鍵
    secret_key: "~/.ssh/ansible_rsa" # 秘密鍵
    login_shell: '/bin/bash'
    create_home: 'yes'
    sudo: 'present'
    comment: 'ansible'
    expires: '-1'
user_groups: # groups
  wheel:
    name: 'wheel'
    state: 'present'
```

### group_vars/conoha/hostname.yml
```yml
hostname: 'example.yourdomain' # As you like
```

### group_vars/conoha/sshs.yml
```yml
sshd_port: 50022 # As you like Default 22
```

### group_vars/conoha/secret.yml 
```yml
secret:
  ansible_user_password: 'User_Password'  # Ansile user password
  softether_ipsec_presharedkey: "Share_key" # As you like
  softether_administrator_password: 'SoftEther_Administrator_Password' #softether admin pass softether_vpn_users:
  # softether ussers
    - {
      name: "worker001",
      password: "workder001_password"
    }
    - {
      name: "worker002",
      password: "workder002_password"
    }
```

### group_vars/conoha/conoha.yml 
For Deploy use conoha API
```yml
conoha_account:
  user: "your_conoha_API_user_name"
  password: "your_API_password"
  tenant: "your_API_tenant_id"
  sec_group: ""
  script_path: ""
conoha_servers:
  -  tag_name: "se_001" # As you like
     server_root_password: "server_root_password"
     sec_group: ""
     script_path: ""
     flavor_name: "g-c1m512d30"  # plan_name. this is example.(512MB,30G)
     image_name: "vmi-centos-7.8-amd64-30gb" # image name. This is example.(CentOS 7.8)
  -  tag_name: "se_002"
     server_root_password: "VV3bD1m3ns10n"
     sec_group: ""
     script_path: ""
     flavor_name: "g-c1m512d30"
     image_name: "vmi-centos-7.8-amd64-30gb"
```

## Test 実行
```bash
./test.py
```
### 振る舞い
- ./Dockerfileよりコンテナー起動 (group_vars/conoha/docker.yml)
- Inventoryfile生成
- docker_client(group_vars/conoha/docker.yml) へ 'docker exec'実行
  - ansile-lint
  - black
  - flake8
  - andible-playook
  - testinfra
  - docker rm 

## Deploy 実行
```bash
./deploy.py
```
### 振る舞い
- conoha insit, Token生成、サーバー追加 (Read group_vars/conoha/conoha.yml)
  deploy/conoha/config へ token.json, servers.json 生成
- ./Dockerfileよりコンテナー(docker_client)起動 (group_vars/conoha/docker.yml)
- Inventoryfile生成 (Read deploy/conoha/config/servers.json)
- docker_client(group_vars/conoha/docker.yml) へ 'docker exec'実行
  - ansile-lint
  - black
  - flake8
  - andible-playook
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