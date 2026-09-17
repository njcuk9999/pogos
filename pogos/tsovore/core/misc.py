#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-10-27 at 13:24

@author: cook
"""
from typing import Dict, List, Literal, Optional
from aperocore.constants import constant_functions
from aperocore.constants import param_functions
from aperocore.core import drs_log
from pogos.core import base as pogos_base
from pogos.core import definitions


# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'tsovore.core.misc'
__version__ = pogos_base.__version__
__date__ = pogos_base.__date__
__authors__ = pogos_base.__authors__
# Get parameter dictionary
ParamDict = param_functions.ParamDict
# Get Logging function
WLOG = drs_log.wlog
# Constants definition
Const = constant_functions.Const
ConstDict = constant_functions.ConstantsDict
STEP_DESCRIPTION = ('Whether to perform the step: {0}. '
                    '\nEach step should contiain the following:'
                    '\n - RUN: bool, whether to run the step'
                    '\n - MODE: str, the mode to use for the step'
                    '\n - KWARGS: dict, any additional keyword arguments'
                    '\n - FNAME: str, the suffix/basename to use'
                    '\n - FTYPE: str, whether FNAME is a suffix or a basename')


# =============================================================================
# Define functions
# =============================================================================
class StepList:
    def __init__(self):
        """
        A list for managing step classes
        """
        self.data: List[Step] = []

    @staticmethod
    def all_modes():
        return list(definitions.ENABLED_INST_MODES)

    @staticmethod
    def not_modes(*reject_modes: str) -> List[str]:
        """
        Way to reject one or a few modes and keep the rest
        """
        # output
        accept_modes = []
        # loop around all modes and get the accepted modes
        for _mode in StepList.all_modes():
            # accepted if not in rejected
            if _mode.name not in reject_modes:
                accept_modes.append(_mode)
        return accept_modes


    def add_step(self, name: str, flavour: str,
                 fname: str,
                 ftype: Literal['suffix', 'common', 'full'],
                 run: bool = True,
                 modes: Optional[List[str]] = None,
                 descs: Optional[Dict[str, str]] = None):
        """
        Add a step straight to the step list via a single call
        """
        self.data.append(Step(name, flavour, fname, ftype,
                              run, modes, descs))

    def to_cdict(self, cdict: ConstDict, source: str, group: str):
        """
        Add all steps to cdict
        """
        # loop around all items and populate cdict
        for item in self.data:
            cdict.add(**item.cdict_kwargs(source, group))

class Step:
    def __init__(self, name: str, flavour: str,
                 fname: str,
                 ftype: Literal['suffix', 'common', 'full'],
                 run: bool = True,
                 modes: Optional[List[str]] = None,
                 descs: Optional[Dict[str, str]] = None):
        # cleaned name
        self.name = name.upper().replace(' ', '_')
        # flavour of the step
        self.flavour = flavour
        # filename or suffix of the step (used to determine skipping)
        self.fname = fname
        # file type for "fname" either "suffix" or "full"
        self.ftype = ftype
        # whether to run this step (if False this step is always skipped)
        self.run = run
        # any kwargs passed to the step (if empty uses default values)
        self.kwargs = dict()
        # deal with modes
        if modes is None:
            self.modes = StepList.all_modes()
        else:
            # check that modes given are valid
            for mode in modes:
                mode_name = mode.name if hasattr(mode, 'name') else mode
                if mode_name not in definitions.MODE_BY_NAME:
                    emsg = f'Step {name} has unsupported mode {mode}'
                    raise pogos_base.PogosException(emsg)
            self.modes = [definitions.MODE_BY_NAME[mode]
                          if isinstance(mode, str) else mode for mode in modes]
        # deal with descs
        if descs is None:
            self.descs = dict()
        else:
            self.descs = descs

    def from_dict(self, data: dict):
        """
        Push a dictionary in and update the step attributes accordingly
        """
        self.run = data['run']
        self.flavour = data['flavour']
        self.kwargs = data['kwargs']
        self.fname = data['fname']
        self.ftype = data['ftype']
        self.modes = [definitions.MODE_BY_NAME[mode]
                  if isinstance(mode, str) else mode
                  for mode in data['modes']]

    def cdict_kwargs(self, source: str, group: str) -> Dict[str, str]:
        """
        For tsovore.py create a dictionary to push into CDict (so steps are
        normal constants)

        """
        # generate the value dictionary
        value = dict()
        value['RUN'] = self.run
        value['FLAVOUR'] = self.flavour
        value['KWARGS'] = self.kwargs
        value['FNAME'] = self.fname
        value['FTYPE'] = self.ftype
        # set the description
        description = str(STEP_DESCRIPTION)
        # deal with flvaour descriptions
        for flavour in self.descs:
            description += (f'\nFlavour={flavour} notes:'
                            f'\n{self.descs[flavour]}\n')
        # generate step name for title
        step_name = self.name.replace('_', ' ').title()
        # push into arguments to add to the call of cdict
        ckwargs = dict()
        ckwargs['name'] = self.name
        ckwargs['value'] = value
        ckwargs['dtype'] = dict
        ckwargs['source'] = source
        ckwargs['group'] = group
        ckwargs['description'] = description.format(step_name)
        ckwargs['user'] = True
        ckwargs['active'] = True
        ckwargs['tex_arg'] = True
        # only add modes if we aren't adding all of them
        if len(self.modes) < len(definitions.ENABLED_INST_MODES):
            ckwargs['modes'] = [mode.name for mode in self.modes]
        # return the ckwargs for pushing to the cdict
        return ckwargs


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # print 'Hello World!'
    print("Hello World!")

# =============================================================================
# End of code
# =============================================================================
