# pogos
PrOcessing General ObServations - A wrapper for PAKORA, SOSSISSE and SORBET

## Table of contents

1. [Installation](#1-installation)


---

## 1. Installation

#### Step 1: Download the GitHub repository

```bash
git clone git@github.com:njcuk9999/sossisse.git
```

or if this doesn't work try:

```bash
git clone https://github.com/njcuk9999/sossisse.git
```

#### Step 2: Make a new environment (recommended)

Using conda, create a new environment and activate it.

Note one can also use venv (instead of conda) or use a current environment but
we recommend a new clean environment to avoid module conflicts.


```bash
conda create --name pogos-env python=3.10
```

```bash
conda activate pogos-env
```

Note you need to activate `pogos-env` each time before running any SOSSISSE command.

#### Step 3: Install sossisse with pip 

Make sure you are in `pogos-env` conda environment (or equivalent) and then run:

```
cd {POGOS_ROOT}

pip install -U -e .[full]
```

Note `{POGOS_ROOT}` is the path to the cloned GitHub repository (i.e. `/path/to/pogos`)
if you are in the directory where you did your `git clone` then you need to change directory into the `pogos` directory.


[Back to top](#table-of-contents)