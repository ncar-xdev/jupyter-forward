# Examples

## Running on a Remote Host's Login Node

For instance, here is how to start a jupyter lab server running one of of Casper's login nodes:

```bash
❯ jupyter-forward mariecurie@casper.ucar.edu
```

<script id="asciicast-368112" src="https://asciinema.org/a/368112.js" async data-speed="2"></script>

## Running on a Remote Host's Compute Node

To launch `jupyter lab` on a remote host's compute node, the user needs to specify the `--launch-command` option. The launch command is meant to submit a job on the remote host's queueing system. Once the job is up and running, `jupyter lab` is launched on the compute node and the session is port-forwarded to the user's local machine.

Here is an example showing how to launch jupyter lab on Cheyenne's compute node.

```{admonition} Note
Cheyenne uses the [PBS job scheduler](https://www.altair.com/pbs-works-documentation/)
```

In the following command, we tell the remote host to use the `qsub` command to submit a batch job to PBS. In addition, we specify the resources, and set job attributes:

- The queue: `-q regular`
- The project account: `-A AABD1115`
- The resources: 1 node, 36 cpus via `-l select=1:ncpus=36,walltime=00:05:00`

```bash
❯ jupyter-forward mariecurie@cheyenne.ucar.edu \
  --launch-command "qsub -q regular -l select=1:ncpus=36,walltime=00:05:00 -A AABD1115"
```

<script id="asciicast-368128" src="https://asciinema.org/a/368128.js" async data-speed="2"></script>

Here's an example showing how to launch jupyter lab on a remote system that uses [Slurm job scheduler](https://slurm.schedmd.com/documentation.html),

```bash
❯ jupyter-forward mariecurie@casper.ucar.edu \
  --launch-command "sbatch -A AABD1115 -t 00:05:00"
```
