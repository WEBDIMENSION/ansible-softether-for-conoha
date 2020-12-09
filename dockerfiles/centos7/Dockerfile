FROM centos:centos7

VOLUME [ "/sys/fs/cgroup" ]
RUN yum -y update; yum clean all
RUN yum -y install openssh-server passwd; yum clean all
RUN yum install -y which
RUN yum install -y https://repo.ius.io/ius-release-el7.rpm
#RUN yum install -y gcc openssl-devel bzip2-devel libffi-devel
#RUN yum install -y python37u python37u-libs python37u-devel python37u-pip
#RUN python3.7 -m pip install --upgrade pip
RUN yum install -y sudo
RUN yum install -y wget
RUN yum install -y curl
RUN yum install -y sshpass
#RUN yum -y install \
#  bzip2 \
#  bzip2-devel \
#  gcc \
#  git \
#  libffi-devel \
#  openssl \
#  openssl-devel \
#  readline \
#  readline-devel \
#  sqlite \
#  sqlite-devel \
#  zlib-devel
#RUN curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
#RUN echo $'\n\
#    export PATH="/root/.pyenv/bin:$PATH"\n\
#    eval "$(pyenv init -)"\n\
#    eval "$(pyenv virtualenv-init -)"\n\
#    ' >> /root/.bashrc
#RUN /root/.pyenv/bin/pyenv install 3.7.6
#RUN /root/.pyenv/bin/pyenv global 3.7.6
#RUN /root/.pyenv/bin/pyenv rehash
#RUN /root/.pyenv/shims/python -m pip install --upgrade pip
#RUN yum install -y jq
#RUN yum install -y sshpass

#RUN pip install ansible
#RUN pip install ansible-lint
#RUN pip install testinfra
#RUN yum install -y openssh-clients

## ユーザーを追加
#RUN useradd kabigon
#RUN echo 'kabigon:password' |chpasswd
#RUN echo "kabigon ALL=(ALL) ALL" >> /etc/sudoers

# rootのパスワードを設定
RUN echo 'root:password' | chpasswd
# SSH
RUN mkdir /root/.ssh
RUN touch /root/.ssh/config
RUN echo $'Host *\n\
 \tStrictHostKeyChecking no\n\
 \n\
ServerAliveInterval 60 \n\
ServerAliveCountMax 10 \n '  >> /root/.ssh/config

RUN chmod 700 /root/.ssh/
RUN chmod 600 /root/.ssh/*

# 22番ポートを外に開ける
#EXPOSE 22

# ホストキーを作成 使わなくても作成する必要がある
RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ''
#ENTRYPOINT ["/usr/sbin/sshd", "-D"]
ENTRYPOINT ["/sbin/init"]
