# Conoha VPS サーバーでVPN (SoftEther) をAnsibleで構築

## 環境
***Local***
- ubuntu 18.04
- ansible 2.9.7 

***Server***
- CentOS 7.8 (Conoha VPS 512MB)

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
  - Hostname 設定 
  - SoftEther インストール
  
## 参考サイト 
- Ansible galaxy  [sa-vpn-softether](https://galaxy.ansible.com/softasap/sa-vpn-softether)
- Github [sa-vpn-softether](https://github.com/softasap/sa-vpn-softether)
***改変箇所***
- AnsibleからSofteher Administrator password を設定できる。
  pipからInstallするpexpectでは意図するうごきならなかったため、
  shellモジュールでexpectを展開させた。

## 設定
### hosts/conoha
```yml
[softether]
# Server IP address
target_server_name ansible_host=xxx.xxx.xxx.xxx

[softether:vars]
ansible_ssh_user=root
ansible_port=22
ansible_ssh_pass={{ secret.root_user_password }}

[conoha]
target_server_name
```

### group_vars/conoha/common.yml
``` yml
# timezone
os_time_zone: "Asia/Tokyo"
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


### group_vars/conoha/sshs.yml
```yml
sshd_port: 50022 #Default 
```

### group_vars/conoha/sshs.yml
```yml
.
.
.

# ============== Users ===================
softether_vpn_users:
  - {
      name: "{{ secret.softether_user }}",
      password: "{{ secret.softether_password }}"
    }
# ============== /Users ===================
.
.
.

```

### group_vars/conoha/secret.yml 
```yml
secret:
  root_user_password: 'Server_Root_Password'
  ansible_user_password: 'User_Password'
  softether_ipsec_presharedkey: "Share_ley"
  softether_administrator_password: 'SoftEther_Administrator_Password'
  softether_user: 'SoftEther_User_Name'
  softether_password: 'SoftEther_User_Password'

  root_user_password: 'Server_Root_Password' #サーバーのルートパスワード
  ansible_user_password: 'User_Password' #サーバーの一般ユーザーパスワード
  softether_ipsec_presharedkey: "Share_Key"  #Ipsec 共有キー
  softether_administrator_password: 'Softether_Administrator_Password' #SoftEtherの管理者パスワード
  
softether_vpn_users:
  - {
    name: "{{ softether_worker001 }}",
    password: "{{ softether_worker001_password }}"
  }
  - {
    name: "{{ softether_worker002 }}",
    password: "{{ softether_worker002_password }}"
  }
```

## Ansible 実行
```bash
ansible-playbook -i hosts/conoha site.yml
```

## クライアントツールのダウンロード
[SoftEther Client](https://www.softether-download.com/en.aspx?product=softether)

----
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