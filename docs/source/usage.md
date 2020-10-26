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

## Examples

### Running on a Remote Host's Login Node

For instance, here is how to start a jupyter lab server running one of of Cheyenne's login nodes:

```bash
❯ jupyter-forward mariecurie@cheyenne.ucar.edu
```

<script id="asciicast-368112" src="https://asciinema.org/a/368112.js" async data-speed="2"></script>

### Running on a Remote Host's Compute Node

To launch `jupyter lab` on a remote host's compute node, the user needs to specify the `--launch-command` option. The launch command is meant to submit a job on the remote host's queueing system. Once the job is up and running, `jupyter lab` is launched on the compute node and the session is port-forwarded to the user's local machine.

Here is an example showing how to launch jupyter lab on Cheyenne's compute node. Cheyenne uses uses [PBS job scheduler](https://www.altair.com/pbs-works-documentation/)

```bash
❯ jupyter-forward mariecurie@cheyenne.ucar.edu --launch-command "qsub -q regular -l select=1:ncpus=36,walltime=00:05:00 -A AABD1115"
```

<script id="asciicast-368128" src="https://asciinema.org/a/368128.js" async data-speed="2"></script>

Here's an example showing how to launch jupyter lab on a remote system that uses [Slurm job scheduler](https://slurm.schedmd.com/documentation.html),

```bash
❯ jupyter-forward mariecurie@casper.ucar.edu --launch-command "sbatch -A AABD1115 -t 00:05:00"
```
