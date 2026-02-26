# pogos
PrOcessing General ObServations: A wrapper for TSOVORE, SOSSISSE, MIRIAM and SORBET

## Table of contents

1. [Introduction](#introduction)
2. [Installation](#1-installation)
3. [Setup POGOS](#2-setting-up-pogos)
4. [Running POGOS](#3-running-pogos)
5. [Running POGOS with your own data](#5-running-pogos-with-your-own-data)
6. [Dev mode](#4-dev-mode)

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
  - SORBET will be able to ingest data from SOSSISSE and MIRIAM

### Important notes:
- POGOS is currently under beta-development, please work with the developers when running the code on new data.
- Note that SOSSISSE can also be run independently of POGOS ([see here](https://github.com/njcuk9999/sossisse)), 
however we strongly recommend using POGOS to run SOSSISSE as it provides a simple interface and demos to set up 
and run SOSSISSE.
- Note also that SOSSISSE requires some additional pre-processing than is provided in the base JWST pipeline, even though
the default input to SOSSISSE is rateints files identical (in format) to those produced by the JWST pipeline.
- Note that currently TSOVORE is under alpha-development and not yet available for use. Please contact [Loic Albert](mailto:loic.albert@umontreal.ca) for more information.
- Note that MIRAM is under alpha-development and not yet available for use. Please contact [Etienne Artigau](mailto:etienne.artigau@umontreal.ca) for more information.

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
git clone https://github.com/njcuk9999/pogos.git
```

#### Step 2: Make a new environment (recommended)

Using conda, create a new environment and activate it.

Note one can also use venv (instead of conda) or use a current environment but
we recommend a new clean environment to avoid module conflicts.


```bash
conda create --name pogos-env python=3.12
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

This should ask you for several options, and create a file structure and a yaml file, based on a demo we supply.
You can and should run this demo (it downloads the data) just to make sure your installation ran correctly.

Once you have run a demo you can either manually edit the demo yaml and copy the file structure we provide, or run `pogos_copy` ([This section](#5-running-pogos-with-your-own-data))
to walk you through creating a new yaml file and file structure based on your own data.

[Back to top](#table-of-contents)

---

## 4. Running POGOS

Once you have run `pogos_setup` and read and understood the yaml file you can run the main POGOS code.
We strongly suggest the first time you run POGOS you do so on the demo data to ensure everything is working correctly.

Running POGOS is as simple as running one command as follows:

```bash
pogos_run --yamlfile={path_to_yaml_file}
```

where `{path_to_yaml_file}` is the path to the yaml file you created in the setup step.


Note once you have run the demo you can run `pogos_run` on your own data ([This section](#5-running-pogos-with-your-own-data)).

[Back to top](#table-of-contents)

--

## 5. Running POGOS with your own data

There are two options to set up POGOS with your own data:
1. Manually edit the demo yaml file and copy the demo file structure to your own data.
2. Use the `pogos_copy` command to walk you through creating a new yaml file and file structure.

To run `pogos_copy` run the following command from inside the `pogos-env` conda environment (or equivalent):

```bash
pogos_copy --demo_file {demo_yaml_file}
```

You will then be asked a set of questions about your data and a new yaml file and file structure will be created for you.
Note for a new instrument/mode combined you will need to run `pogos_setup` first to create a demo for that mode 
(we recommend again that you test the demo first to ensure your installation is working correctly).


[Back to top](#table-of-contents)

--

## 6. Dev mode

For dev mode (editable install of both apero-core and sossisse) please run the following:

```bash
conda create --name pogos-env python=3.12
conda activate pogos-env

pip install radvel

git clone git@github.com:njcuk9999/apero-drs.git -b v0.8.running
git clone git@github.com:njcuk9999/sossisse.git -b developer
git clone git@github.com:njcuk9999/pogos.git -b developer

pip install -U -e './apero-drs/apero-core'
pip install -U -e './sossisse[dev]'
pip install -U -e './pogos[dev]'
```

And then proceed with [Setup](#2-setting-up-pogos) and [Running](#3-running-pogos) POGOS.


**IMPORTANT NOTE:**

When running in dev mode you must ensure that you are NOT in a directory
that contains directories called "aperocore", "sossisse" or "pogos" as this will
cause python to try and import from the local directories instead of the
installed packages (this includes the ones you cloned above).

[Back to top](#table-of-contents)

---
