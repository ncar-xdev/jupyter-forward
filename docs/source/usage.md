# Usage

`jupyter-forward` provides functionality to launch a jupyter lab session on a remote cluster via the `jupyter-forward` command:

```bash
❯ jupyter-forward --help
Usage: jupyter-forward [OPTIONS] HOST

  Starts Jupyter lab on a remote resource and port forwards session to local
  machine.

Arguments:
  HOST  [required]

Options:
  --port INTEGER                  The local port the remote notebook server
                                  will be forwarded to. If not specified,
                                  defaults to 8888.  [default: 8888]

  --conda-env TEXT                Name of the conda environment on the remote
                                  host that contains jupyter lab.

  --notebook-dir TEXT             The directory on the remote host to use for
                                  notebooks. Defaults to $HOME.

  --port-forwarding / --no-port-forwarding
                                  Whether to set up SSH port forwarding or
                                  not.  [default: True]

  -i, --identity PATH             Selects a file from which the identity
                                  (private key) for public key authentication
                                  is read.

  -c, --launch-command TEXT       Custom command to run before launching
                                  Jupyter Lab. For instance: "qsub -q regular
                                  -l select=1:ncpus=36,walltime=00:05:00 -A
                                  AABD1115"

  -s, --shell TEXT                Which remote shell binary to use.  [default:
                                  /usr/bin/env bash]

  --version                       Display jupyter-forward version
  --install-completion            Install completion for the current shell.
  --show-completion               Show completion for the current shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.
```

## Authentication

`jupyter-forward` **doesn't implement** any authentication logic. `jupyter-forward` relies on remote host's SSH authentication mechanism. Therefore, `jupyter-forward` supports most if not all SSH authentication mechanisms:

- Password based authentication
- Password/passphrase + Two-factor authentication (Duo, Yubikey, etc) for SSH
- Passwordless authentication via public-private key pairs
