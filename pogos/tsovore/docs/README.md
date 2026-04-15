# README for TSOVORE

## Contents

- [How to add a new step in process](how-to-add-a-new-step-in-process)
- [How to remove a step in process](how-to-remove-a-step-in-process)


## How to add a new step in process

### Step 1

Choose which instrument class you wish to add a step to and locate the `process` method in the class definition. For example, if you want to add a step to the `Telescope` class, you would find the `process` method.

### Step 2

Add your new step to the `process` method. This could be a new function call, a new data manipulation step, or any other operation you want to perform on the data. Make sure to follow the existing structure and conventions used in the `process` method.


### Step 3

Make sure your method has the following at the top
```python
        # set function name
        func_name = f"{__NAME__}.[class_name].[func_name]"
        # ---------------------------------------------------------------------
        # Do not modify this step
        # ---------------------------------------------------------------------
        # initialize step (do not modify)
        rkwargs = self.assign_step(infiles, func_name)
        if not rkwargs['RUN_STEP']: return rkwargs['INFILES']
        # ---------------------------------------------------------------------
```
where [class_name] is the name of the class where you are adding this method (usually Tso)
where [func_name] is the name of the function you are adding (e.g. in process you would write self.[func_name]). [func_name] should be all in lower case here.

[func_name] should not have any punctuation other than underscores.

Note it is very important that the `func_name` is correct we use `.split('.')[-1].upper()` to denote the `[FUNC_NAME]` throughout so please make sure it works.

### Step 4

After adding your new step, go into pogos/constants/tsovore.py


### Step 5

Add a new step in the following way (near the bottom of tsovore.py):
```python

# description for initialize detector data
jwst_initialize_desc = 'No kwargs for initialization step'
# Initialize detector data
STEPS.add_step(name='INITIALIZE_DETECTOR_DATA',
               flavour='jwst', fname='_saturationstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.all_modes(),
               descs=dict(jwst=jwst_initialize_desc))

```

Add the step in a logical order (this isn't inforced but helps readability)

All values are the **default** values put into the yaml files - any user can change these values (except descs)

- where `name=[FUNC_NAME]` is the uppercase form of [func_name]

- where `flavour` is the flavour of the step
  - this will probably be `=tso` in most cases but `jwst` is the default)
  - Note this can be used so we have two or more "ways" of processing inside the step. 
  - One could imagine having a step name that is already suitable for the task at hand and one wants to give two ways of doing this. 

- where `fname`+`ftype` is usually the suffix appended to the end of the prefixes 
(prefixes are the basename before `_uncal.fits`)
  - if this step produces one file per `uncal` file this is the preferred method (and you must set `ftype=suffix`). 
  - However use `ftype=full` for the full basename file. 
  - Note that this `fname` is what is used to determine whether we skip a step. 
  - If the prefix + suffix or full file name is in the PATHS.TEMP_PATH then this skip wil be skipped. 
  - If filename is None this step can never be skipped - no files are produced (not recommended). 

- IMPORTANT: if `ftype=full` you should always return the infiles

- where `run` is True to run by default (if False by default this step will not be run)

- where `modes` is a list of instrument modes that this step is to be used in. 
  - If None all modes are given. 
  - If set only these modes can be used (other modes will skip this step)
  - There are two useful helper functions `STEPS.all_modes()` and `STEPS.not_modes()`
  - `STEPS.all_modes()` pushes all instrument modes into `modes`
  - `STEPS.not_modes(arg1, arg2)` pushes all instrument modes except arg1, arg2

- where `descs` is a dictionary for each "flavour"
  - if this is added this will be added to the description pushed to the user yaml file

## How to remove a step in process

### Step 1

Choose which instrument class you wish to add a step to and locate the `process` method in the class definition. For example, if you want to add a step to the `Telescope` class, you would find the `process` method.

### Step 2

Delete step or comment out step in the `process` method. 

### Step 3

After adding your new step, go into pogos/constants/tsovore.py

### Step 4

Change the `mode` parameter in the correct step:

```python
# description for initialize detector data
jwst_initialize_desc = 'No kwargs for initialization step'
# Initialize detector data
STEPS.add_step(name='INITIALIZE_DETECTOR_DATA',
               flavour='jwst', fname='_saturationstep.fits',
               ftype='suffix', run=True,
               modes=STEPS.all_modes(),
               descs=dict(jwst=jwst_initialize_desc))
```

  - There are two useful helper functions `STEPS.all_modes()` and `STEPS.not_modes()`
  - `STEPS.all_modes()` pushes all instrument modes into `modes`
  - `STEPS.not_modes(arg1, arg2)` pushes all instrument modes except arg1, arg2
  - Or you can just enter a single value in the list if only one mode is now supported

Or if the step is no longer needed in any mode remove the STEPS.add_step entry for this step.


