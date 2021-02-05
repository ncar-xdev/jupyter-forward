# Development Guide

## Provisioning the vagrant VM environment

```bash
vagrant up
vagrant ssh-config > vagrant-ssh
ssh -F vagrant-ssh default
```

## Launching jupyter-forward

```bash
jupyter-forward vagrant@127.0.0.1:2222 --identity ./.vagrant/machines/default/virtualbox/private_key
```
