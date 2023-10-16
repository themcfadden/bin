ARG VERSION=latest
FROM ubuntu:$VERSION

# Fix "Couldn't register with accessibility bus" error message
ENV NO_AT_BRIDGE=1

ENV DEBIAN_FRONTEND noninteractive

# basic stuff
RUN echo 'APT::Get::Assume-Yes "true";' >> /etc/apt/apt.conf \
    && apt-get update && apt-get install \
    apt-utils \
    bash \
    build-essential \
    dbus-x11 \
    fontconfig \
    git \
    gzip \
    language-pack-en-base \
    libgl1-mesa-glx \
    make \
    sudo \
    tar \
    unzip \
    curl \
    openssl \
    openssh-server \
    ripgrep \
    fd-find \
    tmux \
    sed \
    clangd \
# su-exec
    && git clone https://github.com/ncopa/su-exec.git /tmp/su-exec \
    && cd /tmp/su-exec \
    && make \
    && chmod 770 su-exec \
    && mv ./su-exec /usr/local/sbin/ \
# Cleanup
    && apt-get purge build-essential \
    && apt-get autoremove \
    && rm -rf /tmp/* /var/lib/apt/lists/* /root/.cache/*

#COPY asEnvUser /usr/local/sbin/    

# Only for sudoers
#RUN chown root /usr/local/sbin/asEnvUser \
#    && chmod 770  /usr/local/sbin/asEnvUser

# ^^^^^^^ Those layers are shared ^^^^^^^

# Emacs
RUN apt-get update && apt-get install software-properties-common \
    && apt-get install emacs \
# Cleanup
    && apt-get purge software-properties-common \
    && rm -rf /tmp/* /var/lib/apt/lists/* /root/.cache/*


ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-server tmux \
    curl git \
    python3 python3-pip python3-virtualenv python3-dev build-essential
RUN apt-get update && \
    apt-get install -y python3 \
    python3-pip \
    python3-virtualenv \
    python3-dev


ENV user emacs
RUN useradd -G sudo -u 1000 --create-home ${user}
RUN adduser ${user} sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ${user}

ENV HOME /home/emacs

ENV UNAME="emacs" \
    GNAME="emacs" \
    UHOME="/home/emacs" \
    UID="1000" \
    GID="1000" \
    WORKSPACE="/mnt/workspace" \
    SHELL="/bin/bash"

RUN echo "PATH=$HOME/.config/emacs/bin:$PATH" >> $HOME/.bashrc && . $HOME/.bashrc

# Emacs Doom
RUN mkdir /home/emacs/.config && \
    git clone --depth 1 https://github.com/doomemacs/doomemacs /home/emacs/.config/emacs && \
    ~/.config/emacs/bin/doom install --no-env && \
    sed -i '/(evil +everywhere)/s/^/;;/' /home/emacs/.config/doom/init.el && \
    sed -i '/;;lsp/s/^ *;;/       /' /home/emacs/.config/doom/init.el && \
    sed -i '/;;tree-sitter/s/^ *;;/       /' /home/emacs/.config/doom/init.el && \
    sed -i '/;;(cc +lsp)/s/^ *;;/       /' /home/emacs/.config/doom/init.el && \
    /home/emacs/.config/emacs/bin/doom sync

CMD ["bash", "-c", "emacs; /bin/bash"]

#
# Create image with:
#
# docker build --tag run-emacs-docker .


#
# Run with this:
# 
##!/bin/bash
#
#xhost +si:localuser:mattmc
#
#docker run -it --rm \
#       --name emacs \
#       -e HOME="/home/emacs" \
#       -e DISPLAY="$DISPLAY" \
#       -e UID="1000" \
#       -e GID="1000" \
#       -w `pwd` \
#       -v /tmp/.X11-unix:/tmp/.X11-unix \
#       -v `pwd`:`pwd` \
#       --user 1000 \
#       --net=host \
#       run-emacs-docker $1 $2
#
#xhost -local:
