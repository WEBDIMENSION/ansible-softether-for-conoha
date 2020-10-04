FROM ubuntu:20.04
RUN apt-get update && \
    apt-get install -y software-properties-common \
                       tzdata

RUN apt-add-repository -y ppa:git-core/ppa && \
    apt-get update && \
    apt-get install -y git \
                       curl \
                       openssh-server \
                       vim \
                       sudo \
                       sshpass \
                       python3-pip
#RUN useradd -u 1000 worker \
# && usermod -s /bin/bash -G adm,sudo worker \
# && echo "worker ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
# && mkdir -p /home/worker
#COPY roles/ansible_user/files//ansible_rsa.pub /home/worker/.ssh/ansible_rsa.pub
#RUN cat /home/worker/.ssh/ansible_rsa.pub >> /home/worker/.ssh/authorized_keys
#RUN  touch /home/worker/.bashrc
#
#RUN echo '\n\
#if [ -n "$BASH_VERSION" ]; then\n\
#    # include .bashrc if it exists\n\
#    if [ -f "$HOME/.bashrc" ]; then\n\
#        . "$HOME/.bashrc"\n\
#    fi\n\
#fi\n\
#if [ -d "$HOME/bin" ] ; then\n\
#    PATH="$HOME/bin:$PATH"\n\
#fi\n\
#if [ -d "$HOME/.local/bin" ] ; then\n\
#    PATH="$HOME/.local/bin:$PATH"\n\
#fi\n\
#' >> /home/worker/.profile
#
RUN mkdir /root/.ssh
RUN echo '\n\
Host *\n\
    StrictHostKeyChecking no\n\
' >> /root/.ssh/config

#RUN chown -R worker.worker /home/worker
RUN chmod 700 /root/.ssh
RUN chmod 600 /root/.ssh/*

RUN echo 'root:root' | chpasswd
#RUN echo "worker:worker" | chpasswd

#WORKDIR /home/worker/ansible
EXPOSE 22
CMD [ "/sbin/init" ]
