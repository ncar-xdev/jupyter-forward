#!/usr/bin/env bash

ssh-keygen -t ed25519 -f ~/.ssh/my_key -N ''
cat > ~/.ssh/config <<EOF
Host localhost.local
    User $USER
    HostName 127.0.0.1
    IdentityFile ~/.ssh/my_key
EOF
echo -n 'from="127.0.0.1" ' | cat - ~/.ssh/my_key.pub > ~/.ssh/authorized_keys
chmod og-rw ~
ls -la ~/.ssh
ssh -o 'StrictHostKeyChecking no' localhost.local id
