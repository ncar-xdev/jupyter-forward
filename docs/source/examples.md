# Examples

## Launching Jupyter Lab on a Remote Host's Login Node

For instance, here is how to start a jupyter lab server running on a login node of a remote host:

```bash
❯ jupyter-forward username@supersystem.univ.edu
```

<script id="asciicast-368112" src="https://asciinema.org/a/368112.js" async data-speed="2"></script>

## Launching Jupyter Lab on a Remote Host's Compute Node

To launch `jupyter lab` on a remote host's compute node, the user needs to specify the `--launch-command` option. The launch command is meant to submit a job on the remote host's queueing system. Once the job is up and running:

1. `jupyter lab` is launched on the compute node
2. the session is port-forwarded to the user's local machine.
3. and a link to the jupyter lab session is opened in the local machine's browser.

Here is an example showing how to launch jupyter lab on Cheyenne's compute node.

```{admonition} Note
Cheyenne uses the [PBS job scheduler](https://www.altair.com/pbs-works-documentation/)
```

In the following command, we tell the remote host to use the `qsub` command to submit a batch job to PBS. In addition, we specify the resources, and set job attributes:

- The queue via `-q regular`
- The project account via `-A AABD1115`
- The resources: 1 node, 36 cpus via `-l select=1:ncpus=36,walltime=00:05:00`

```bash
❯ jupyter-forward username@supersystem.univ.edu \
  --launch-command "qsub -q regular -l select=1:ncpus=36,walltime=00:05:00 -A AABD1115"
```

<script id="asciicast-368128" src="https://asciinema.org/a/368128.js" async data-speed="2"></script>

Here's an example showing how to launch jupyter lab on a remote system that uses [Slurm job scheduler](https://slurm.schedmd.com/documentation.html),

```bash
❯ jupyter-forward username@supersystem.univ.edu \
  --launch-command "salloc -A AABD1115 -t 00:05:00 srun"
```

## Launching Jupyter Lab on a Remote Host without port-forwarding

If and/or when the remote host has nodes that can be accessed via a public IP address, `jupyter-forward` provides a `--no-port-forwarding` option which disables SSH tunneling. When the `--no-port-forwarding` option is active, the Jupyter Lab session is accessible at `https:\\<public-ip-address:port>` instead of `https:\\<localhost:port>` in the local machine's browser.

```bash
❯ jupyter-forward username@supersystem.univ.edu --no-port-forwarding
```

<script id="asciicast-368157" src="https://asciinema.org/a/368157.js" async data-speed="2"></script>
