# pogos
PrOcessing General ObServations: A wrapper for TSOVORE, SOSSISSE, MIRIAM and SORBET

## Table of contents

1. [Introduction](#introduction)
2. [Installation](#1-installation)
3. [Setup POGOS](#2-setting-up-pogos)
4. [Running POGOS](#3-running-pogos)
5. [Dev mode](#4-dev-mode)

---

## 2. Introduction

**POGOS** (PrOcessing General ObServations) is a python package that wraps around 
several exoplanet data analysis packages to provide a  simple interface for 
processing JWST time-series data.

It is currently separated into several parts:
- **TSOVORE**: A package to  "pre-process" JWST time-series data (it also includes a JWST simulator)
  - **TSOVORE:SIM** is the simulation package
  - **TSOVORE:IMCAL** is the pre-processing package (similar to JWST pipeline stage 1 and some of stage 2)
- **SOSSISSE** (SOSS Inspired SpectroScopic Extraction): A package to extract spectra from JWST time-series data.
  - This is similar to some of the functionality of the JWST pipeline stage 2 and 3 but is optimised for time-series data and extract is handled differentially which is unique amongst JWST pipelines.
- **MIRIAM** (MIRI Imaging Analysis Module): A package to extract photometry from JWST:MIRI time-series data.
- **SORBET** (Suite Of Reduction tools for Both Eclipse and Transit): A package to fit lightcurves and extract transit depths from JWST time-series data.
  - This is similar to some of JWST pipeline stage 3 and what some would call stage 4.

Note that SOSSISSE can also be run independently of POGOS ([see here](https://github.com/njcuk9999/sossisse)), 
however we strongly recommend using POGOS to run SOSSISSE as it provides a simple interface and demos to set up 
and run SOSSISSE.

Note also that SOSSISSE requires some additional pre-processing than is provided in the base JWST pipeline, even though
the default input to SOSSISSE is rateints files identical (in format) to those produced by the JWST pipeline.

Note that currently TSOVORE is under alpha-development and not yet available for use. Please contact [Loic Albert](mailto:loic.albert@umontreal.ca) for more information.
Note that MIRAM is also under alpha-development and not yet available for use. Please contact [Etienne Artigau](mailto:etienne.artigau@umontreal.ca) for more information.

All other issues should be reported to the [GitHub issues page](https://github.com/njcuk9999/pogos/issues).

---

## 2. Installation

Note if you are a developer please see [Dev mode](#4-dev-mode)

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
conda create --name pogos-env python=3.11
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

---

## 3. Setting up POGOS

From inside the `pogos-env` conda environment (or equivalanet), in any directory (except the directory where you downloaded the github directories), run:

```bash
pogos_setup
````

This should ask you for several options, and create a file structure and a yaml file.

[Back to top](#table-of-contents)

---

## 4. Running POGOS

Once you have run `pogos_setup` and read and understood the yaml file you can run the main POGOS code.

You can do this as follows:

```bash
pogos_run {path_to_yaml_file}
```

where `{path_to_yaml_file}` is the path to the yaml file you created in the setup step.


[Back to top](#table-of-contents)

---

## 5. Dev mode

For dev mode (editable install of both apero-core and sossisse) please run the following:

```bash
conda create --name pogos-env python=3.11
conda activate pogos-env

pip install radvel

git clone git@github.com:njcuk9999/apero-drs.git -b v0.8.003
git clone git@github.com:njcuk9999/sossisse.git -b developer
git clone git@github.com:njcuk9999/pogos.git -b developer

pip install -U -e './apero-drs/apero-core'
pip install -U -e './sossisse[dev]'
pip install -U -e './pogos[dev]'
```

And then proceed with [Setup](#2-setting-up-pogos) and [Running](#3-running-pogos) POGOS.

[Back to top](#table-of-contents)

---