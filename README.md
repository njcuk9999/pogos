# pogos
PrOcessing General ObServations: A wrapper for TSOVORE, SOSSISSE, MIRIAM and SORBET

## Table of contents

1. [Installation](#1-installation)
2. [Dev mode](#2-dev-mode)

---

## 1. Installation

Note if you are a developer please see [Dev mode](#2-dev-mode)

#### Step 1: Download the GitHub repository

```bash
git clone git@github.com:njcuk9999/pogos.git
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


## 2. Dev mode

For dev mode (editable install of both apero-core and sossisse) please run the following:

```bash

git clone git@github.com:njcuk9999/apero-drs.git -b v0.8.003
git clone git@github.com:njcuk9999/sossisse.git -b developer
git clone git@github.com:njcuk9999/pogos.git -b developer

pip install -U -e './apero-drs/apero-core'
pip install -U -e './sossisse[dev]'
pip install -U -e './pogos[dev]'
```


[Back to top](#table-of-contents)

---