#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-05-14 at 09:56

@author: cook
"""
import sys

from aperocore.constants import load_functions
import sossisse

from pogos.constants.constants import CDict
from pogos.core import base as pbase
from sossisse.instruments import Instrument

from pogos.recipes import pogos_run

# =============================================================================
# Define variables
# =============================================================================

# -----------------------------------------------------------------------------

# =============================================================================
# Define functions
# =============================================================================
def sossisse_init(yaml_file: str) -> Instrument:
    # force argument
    cmd_kwargs = dict()
    cmd_kwargs['yamlfile'] = yaml_file
    # Define variables
    __NAME__ = pogos_run.__NAME__
    __PACKAGE__ = pogos_run.__PACKAGE__
    __version__ = pogos_run.__version__
    __authors__ = pogos_run.__authors__
    __date__ = pogos_run.__date__
    __release__ = pogos_run.__release__
    # set description
    __description__ = pogos_run.__description__
    __inputs__ = pogos_run.__inputs__
    # get parameters
    params = load_functions.get_all_params(name=__NAME__,
                                           description=__description__,
                                           inputargs=__inputs__,
                                           param_file_path='GLOBAL.YAML_FILE',
                                           config_list=[CDict],
                                           external_const=pbase.EXTERNAL_CONST,
                                           cmd_kwargs=cmd_kwargs)
    # get the SOSSISSE sub-dictionary
    sossisse_params = params.get('SOSSISSE')
    # convert to independent parameter dictionary
    sparams = sossisse_params.as_param_dict()
    # make sure yaml file is set
    sparams['INPUTS.PARAM_FILE'] = str(params['GLOBAL.YAML_FILE'])
    # get instrument class for SOSSISSE
    inst = sossisse.get_parameters(__NAME__=__NAME__, __YAML_DICT__=sparams)


    # force plots to do what we want
    inst.params.set('PLOTS.SHOW', value=True)
    # return SOSSISSE instrument instance
    return inst


# =============================================================================
# Start of code
# =============================================================================
# Main code here
if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # set the yaml file
    yaml_file = '/scratch3/jwst/pogos-data/soss_test.yaml'
    # pogos sossisse init
    inst = sossisse_init(yaml_file)

# =============================================================================
# End of code
# =============================================================================
