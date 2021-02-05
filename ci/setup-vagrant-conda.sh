#!/usr/bin/env bash
set -ex

LANG=C.UTF-8 LC_ALL=C.UTF-8
CONDA_DIR=/home/vagrant/opt/conda
PATH=/home/vagrant/opt/conda/bin:$PATH


echo "Installing Apt-get packages..."
echo 'deb https://pkg.duosecurity.com/Ubuntu precise main' > /etc/apt/sources.list.d/duosecurity.list
curl -s https://duo.com/DUO-GPG-PUBLIC-KEY.asc | apt-key add -
apt-key adv --keyserver hkp://keyserver.ubuntu.com --recv-keys 01EF98E910448FDB
apt-get update --fix-missing
apt-get install -y wget bzip2 ca-certificates libglib2.0-0 duo-unix \
        libxext6 libsm6 libxrender1 git mercurial nano vim subversion

echo "Installing Miniconda..."
wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
/bin/bash ~/miniconda.sh -b -p ${CONDA_DIR} -u
rm ~/miniconda.sh
ln -sf ${CONDA_DIR}/etc/profile.d/conda.sh /etc/profile.d/conda.sh
echo ". ${CONDA_DIR}/etc/profile.d/conda.sh" >> ~/.bashrc
echo ". ${CONDA_DIR}/etc/profile.d/conda.sh ; conda activate base" > /etc/profile.d/init_conda.sh
echo "conda activate base" >> ~/.bashrc
conda init bash
${CONDA_DIR}/bin/conda config --set always_yes true --set changeps1 false
${CONDA_DIR}/bin/conda config --add channels conda-forge
${CONDA_DIR}/bin/conda install -c conda-forge jupyterlab
${CONDA_DIR}/bin/conda create -n jupyter-forward-dev jupyterlab -c conda-forge
${CONDA_DIR}/bin/conda list
