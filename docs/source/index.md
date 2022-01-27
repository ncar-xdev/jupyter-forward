# Welcome to jupyter-forward's documentation!

Jupyter-forward simplifies the process of running `jupyter lab` on a remote machine by performing the following tasks on behalf of the users:

1. Logging into a remote cluster/resource via the SSH protocol.
2. Launching Jupyter Lab on the remote cluster.
3. Port forwarding Jupyter Lab session back to your local machine.
4. Opening the port forwarded Jupyter Lab session in your local browser.

## Get in touch

- If you encounter any errors or problems with **jupyter-forward**, please open an issue at the GitHub [main repository](http://github.com/ncar-xdev/jupyter-forward/issues).
- If you have a question like "How do I find x?", ask on [GitHub discussions](https://github.com/ncar-xdev/jupyter-forward/discussions). Please include a self-contained reproducible example if possible.

```{toctree}
---
maxdepth: 1
hidden:
---

tutorials/index.md
how-to/index.md
explanation/index.md
reference/index.md

```

```{toctree}
---
maxdepth: 2
caption: Contribute to jupyter-forward
hidden:
---

contributing.md
changelog.md
GitHub Repo <https://github.com/ncar-xdev/jupyter-forward>
GitHub discussions <https://github.com/ncar-xdev/jupyter-forward/discussions>

```
