#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SORBET: Suite Of Reduction tools for Both Eclipse and Transit

# CODE DESCRIPTION HERE

Created on 2024-10-29 at 09:30

@author: cook
"""
import os
import site

from aperocore.constants import constant_functions

from pogos.core import base

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'pogos.constants.constants.py'
__PACKAGE__ = base.__PACKAGE__
__version__ = base.__version__
__authors__ = base.__authors__
__date__ = base.__date__
__release__ = base.__release__

# Constants definition
Const = constant_functions.Const
ConstDict = constant_functions.ConstantsDict

# =============================================================================
# Constants for SORBET: Suite Of Reduction tools for Both Eclipse and Transit
# =============================================================================
SORBET_CDict = ConstDict(__NAME__)

# set the title for output yaml files
SORBET_CDict.title = SORBET_CDict.yaml_title('SORBET: Suite Of Reduction tools '
                                            'for Both Eclipse and Transit',
                                     setup_program=None,
                                     version=base.SORBET_VERSION,
                                     date=base.SORBET_DATE)

# set the group for all general constants
cgroup = 'GENERAL'
SORBET_CDict.add_group(cgroup, description='General configs for SORBET',
                source=__NAME__, user=True, active=True)
# add the subdirectory (to be used when default path required)
SORBET_CDict.add('SUBDIRECTORY', value=None, dtype=str, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='The sub-directory to use for this SORBET run. '
                             'This should be descriptive and unique. '
                             '\nIt should contain no whitespaces or special '
                             'characters other than underscoes.'
                             '\nAll miriam data will be stored in '
                             '{GLOBAL.DATA_PATH}/sorbet/{SUBDIRECTORY}/'
                             '\n\nWe suggest {OBJNAME}-{INST.MODE}-{STEP}-{YYYYMMDD}')

# define what we are running through SORBET
SORBET_CDict.add('DESCRIPTION', value='', dtype=str, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Description of the POGOS run e.g. object name, '
                             'date of observation, is it a transit or '
                             'an eclipse etc.')


# define the valid Juilet distributions
jdists = ['fixed', 'uniform', 'loguniform', 'normal', 'truncatednormal', 'beta']
SORBET_CDict.add('JULIET_VALID_DISTS', value=jdists, dtype=list, dtypei=str,
                 source=__NAME__, user=False, active=False, group=cgroup,
                 description='Valid prior distributions in juliet')


# =============================================================================
# Definition of inputs related to plots
# =============================================================================
cgroup = 'PLOTS'
SORBET_CDict.add_group(cgroup,
                       description='Definition of inputs related to plots',
                       source=__NAME__, user=True, active=True)
# -----------------------------------------------------------------------------
# Or you can use the following to always show plots regardless of the username
SORBET_CDict.add('SHOW', value=False, dtype=bool,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Or you can use the following to always show '
                             'plots regardless of the username')
# -----------------------------------------------------------------------------
# output(s) type of figure
SORBET_CDict.add('FIGURE_TYPES', value=['png', 'pdf'], dtype=list, dtypei=str,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='output(s) type of figure')

# =============================================================================
# Constants for SORBET white light curve transit analysis
# =============================================================================
# set the group for all WLCA constants
cgroup = 'WLCA'
SORBET_CDict.add_group(cgroup, description='Configs for SORBET.WLCA: White '
                                          'light curve transit analysis',
                source=__NAME__, user=True, active=True)
# Input data path
SORBET_CDict.add('INPUT_PATH', value=f'wlca{os.sep}inputs',
                 dtype=str, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Input data path. If not absolute path'
                             ' it will be set to GLOBAL.DATA_PATH/'
                             'sorbet/{SUBDIRECTORY}/wlca/{INPUT_PATH}/')
# Input data file
SORBET_CDict.add('INPUT_FILE', value='white_light_curve.fits', dtype=str,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Input data file or path to the data file')
# Output sub directory path for channel/bin (set internally)
SORBET_CDict.add('OUTPUT_SUBPATH', value=None, dtype=str, source=__NAME__,
                user=False, active=False, group=cgroup,
                description='Output sub-directory path for channel/bin. '
                            '(set internally)')
# Output results folder
SORBET_CDict.add('OUTPUT_PATH', value=f'wlca{os.sep}outputs', dtype=str,
                source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Output result folder or path to the output folder.'
                            '\nIf this is an aboslute path it will be used as is'
                            '\n otherwise it will be relative to '
                            'GLOBAL.DATA_PATH/sorbet/'
                            '{SUBDIRECTORY}/wlca/{OUTPUT_PATH}/')

# Whether to use previous juliet files (warning this will mean juliet ignores
# any updates to parameters set here)
# Setting this to True will make Juliet run much
# faster but use at your own risk!
SORBET_CDict.add('USE_PREV_JULIET', value=False, dtype=bool, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Whether to use previous juliet temporary files '
                             '(warning this will mean juliet ignores any '
                             'updates to parameters set here). '
                             '\nSetting this to True will make Juliet run much '
                             'faster but use at your own risk!')

# Plot path
SORBET_CDict.add('PLOT_PATH', value=f'wlca{os.sep}plots', dtype=str,
                source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Output plot folder or path to the output folder.'
                            '\nIf this is an aboslute path it will be used as is'
                            '\n otherwise it will be relative to '
                            'GLOBAL.PLOT_PATH/sorbet/'
                            '{SUBDIRECTORY}/wlca/{PLOT_PATH}/')

# Juliet parameters
jps_desc = """
Juliet transit parameters as a list, following the juliet docs
(juliet.readthedocs.io/en/latest/user/priorsnparameters.html). e.g.:
JULIET_PARAMETERS:
 - P_p1
 - t0_p1
 - p_p1
 - b_p1
 - a_p1
 - ecc_p1
 - Pomega_p1
 - q1_{INST_MODE}
 - q2_{INST_MODE}
 - mdilution_{INST_MODE}
 - mflux_{INST_MODE}
 - sigma_w_{INST_MODE}
 
Note those parameters that need an instrument should have _{INST_MODE} instead
of instrument name. Please do not remove or change _{INST_MODE} as this is 
used internally to replace with the instrument name.
"""

SORBET_CDict.add('JULIET_PARAMETERS', value=None, dtype=list, dtypei=str,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=jps_desc)
# Prior distributions
jpd_desc = """
Juliet prior distributions following the juliet docs.
https://juliet.readthedocs.io/en/latest/user/priorsnparameters.html#priors

Values should be one of:
    fixed, uniform, loguniform, normal, truncatednormal, beta

If a distribution is missing from Juliet you can add and override
JULIET_VALID_DISTS e.g.
    SORBET:
        GENERAL:
            JULIET_VALID_DISTS:
            - fixed
            - uniform
            - loguniform
            - normal
            - truncatednormal
            - beta
    Adding any extra required

You must have at least the values in JULIET_PARAMETERS defined

(extras will be ignored). e.g.:
    JULIET_PRIOR_DISTS:
     P_p1: fixed
     t0_p1: uniform
     p_p1: uniform
     b_p1: uniform
     a_p1: uniform
     ecc_p1: fixed
     omega_p1: fixed
     q1_{INST_MODE}: uniform
     q2_{INST_MODE}: uniform
     mdilution_{INST_MODE}: fixed
     mflux_{INST_MODE}: fixed
     sigma_w_{INST_MODE}: loguniform

Note going from Juliet format to SORBET format is easy:

    JULIET_PRIOR_DISTS = dict(zip(juilet_params, juliet_prior_dists))

where juilet_params and juliet_prior_dists are the lists used in juliet
"""

SORBET_CDict.add('JULIET_PRIOR_DISTS', value=None, dtype=dict, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description=jpd_desc)
# Prior values
jpv_desc = """
Juliet prior hyperparameters following the juliet docs.
https://juliet.readthedocs.io/en/latest/user/priorsnparameters.html#priors

You must have at least the values in JULIET_PARAMETERS defined
(extras will be ignored). e.g.:
    JULIET_PRIOR_VALS:
     P_p1: val
     t0_p1: [a, b]
     p_p1: [a, b]
     b_p1: [a, b]
     a_p1: [a, b]
     ecc_p1: val
     omega_p1: val
     q1_{INST_MODE}: [a, b]
     q2_{INST_MODE}: [a, b]
     mdilution_{INST_MODE}: val
     mflux_{INST_MODE}: val
     sigma_w_{INST_MODE}: [a, b]

Note going from Juliet format to SORBET format is easy:

    JULIET_PRIOR_VALS = dict(zip(juilet_params, juliet_prior_values))

where juilet_params and juliet_prior_values are the lists used in juliet
"""

SORBET_CDict.add('JULIET_PRIOR_VALS', value=None, dtype=dict, source=__NAME__,
                user=True, active=True, group=cgroup,
                description=jpv_desc)

# Linear detrending
SORBET_CDict.add('LINEAR_DETRENDING', value=None, dtype=str, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Enable linear detrending of the flux. '
                 '\nSet this value to "time" for temporal slope or '
                 '\n\tprovide the path to a file with the variable to '
                 '\n\tdetrend linearly in each column.'
                 '\nIf using a file LINEAR_DETRENDING_TYPE should be set to '
                 '\n\tthe type of file provided e.g. '
                 '\n\tfile:fits, file:ecsv, file:csv, file:ascii'
                 '\nNote the file should contain N columns, each column will '
                 '\n\tbe used as a detrending variable.')
# Linear detrending type
SORBET_CDict.add('LINEAR_DETRENDING_TYPE', value='null', dtype=str,
                 options=['null', 'file:fits', 'file:ecsv', 'file:csv',
                          'file:ascii'],
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Define the type of linear detrending to apply. '
                             '\nSet this to "null" if no linear detrending '
                             '\n or if the variable to detrend is "time". ')
# Sampling options
SORBET_CDict.add('SAMPLING_OPTIONS', value='dynesty', dtype=str, source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Sampling options in juliet')

# Outlier kernel size
SORBET_CDict.add('OUTLIER_KERNEL_SIZE', value=None, dtype=int, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Define the kernel size (number of time steps '
                             '\nto consider) when running on median filter on '
                             '\nthe time-series to flag outliers. If not set'
                             '\n5% the length of the vector will be used.')
# Debug parameter
SORBET_CDict.add('DEBUG', value=False, dtype=bool, source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Enable debugging')

# =============================================================================
# Constants for SORBET spectral light curve transit analysis
# =============================================================================
# set the group for all SLCA constants
cgroup = 'SLCA'
SORBET_CDict.add_group(cgroup, description='Configs for SORBET.SLCA: '
                                          'Spectral light curve transit '
                                          'analysis',
                source=__NAME__, user=True, active=True)
# Input data path
SORBET_CDict.add('INPUT_PATH', value=f'slca{os.sep}inputs',
                 dtype=str, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Input data path. If not absolute path'
                             ' it will be set to GLOBAL.DATA_PATH/'
                             'sorbet/{SUBDIRECTORY}/{INPUT_PATH}/')
# Input data file
SORBET_CDict.add('INPUT_FILE', value=['spectroscopy_light_curves.fits'],
                 dtype=list, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Input data file or path to the data file')
# Trace orders, must be a list the same length as INPUT_FILE
#     (Set each item to 1 if there is only one order) otherwise set each item
#     to the order number
SORBET_CDict.add('TRACE_ORDERS', value=[1], dtype=list, dtypei=int,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description='Trace orders, must be a list the same length as'
                             'INPUT_FILE '
                             '\n\t(Set each item to 1 if there is '
                             'only one order) otherwise set each item '
                             'to the order number')
# Output sub directory path for channel/bin (set internally)
SORBET_CDict.add('OUTPUT_SUBPATH', value=None, dtype=str, source=__NAME__,
                user=False, active=False, group=cgroup,
                description='Output sub-directory path for channel/bin. '
                            '(set internally)')
# Output results folder
SORBET_CDict.add('OUTPUT_PATH', value=f'slca{os.sep}outputs',
                 dtype=str, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Output result folder or path to the output folder.'
                             '\nIf this is an aboslute path it will be used as is'
                             '\n otherwise it will be relative to '
                             'GLOBAL.DATA_PATH/sorbet/'
                             '{SUBDIRECTORY}/slca/{OUTPUT_PATH}/')

# Whether to use previous juliet files (warning this will mean juliet ignores
# any updates to parameters set here)
# Setting this to True will make Juliet run much
# faster but use at your own risk!
SORBET_CDict.add('USE_PREV_JULIET', value=False, dtype=bool, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Whether to use previous juliet temporary files '
                             '(warning this will mean juliet ignores any '
                             'updates to parameters set here). '
                             '\nSetting this to True will make Juliet run much '
                             'faster but use at your own risk!')

# Plot path
SORBET_CDict.add('PLOT_PATH', value=f'slca{os.sep}plots',  dtype=str,
                source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Output plot folder or path to the output folder.'
                            '\nIf this is an aboslute path it will be used as is'
                            '\n otherwise it will be relative to '
                            'GLOBAL.PLOT_PATH/sorbet/'
                            '{SUBDIRECTORY}/wlca/{PLOT_PATH}/')

# Resolution to bin the spectral light curves
SORBET_CDict.add('RESOLUTION_BIN', value=100, dtype=int, source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Define the spectral resolution to bin to prior to fitting. '
                'For native resolution set to -1')

# Juliet parameters
SORBET_CDict.add('JULIET_PARAMETERS', value=None, dtype=list, dtypei=str,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=jps_desc)
# Prior distributions
SORBET_CDict.add('JULIET_PRIOR_DISTS', value=None, dtype=dict, dtypei=str,
                 source=__NAME__, user=True, active=True, group=cgroup,
                 description=jpd_desc)
# Prior values
SORBET_CDict.add('JULIET_PRIOR_VALS', value=None, dtype=dict, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description=jpv_desc)

# Linear detrending
SORBET_CDict.add('LINEAR_DETRENDING', value=None, dtype=str, source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Enable linear detrending of the flux. '
                '\nTemporal slope is accepted (value=time) or provide the path '
                '\nto a file with the variable to detrend linearly '
                'in each column.')

# Sampling options
SORBET_CDict.add('SAMPLING_OPTIONS', value='dynesty', dtype=str, source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Sampling options in juliet')

# Outlier kernel size
SORBET_CDict.add('OUTLIER_KERNEL_SIZE', value=None, dtype=int, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Define the kernel size (number of time steps '
                             '\nto consider) when running on median filter on '
                             '\nthe time-series to flag outliers. If not set'
                             '\n5% the length of the vector will be used.')
# -----------------------------------------------------------------------------
# ExoTiC-LD
cgroup = 'SLCA.EXOTIC-LD'
SORBET_CDict.add_group(cgroup,
                description='Limb-darkening modeling using the ExoTiC-LD '
                            'package (for transit fitting)',
                source=__NAME__, user=True, active=True)
# Use ExoTiC-LD
SORBET_CDict.add('ENABLE', value=False, dtype=bool, source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Enable limb-darkening modeling with ExoTiC-LD')
# Path to the ExoTiC-LD data directory
SORBET_CDict.add('LD_LAW', value='kipping', dtype=str, source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Select limb-darkening law')
# Path to the ExoTiC-LD data directory
default_value = site.getsitepackages()[0] + '/exotic_ld/exotic-ld_data'
SORBET_CDict.add('MODEL_PATH', value=default_value, dtype=str, source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Path to the ExoTiC-LD data directory')
# ExoTiC-LD model grid
SORBET_CDict.add('MODEL_GRID', value='phoenix', dtype=str, source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Select the ExoTiC-LD model grid to use')
# Stellar metallicity [M/H] (dex)
SORBET_CDict.add('STELLAR_MET', value=0.0, dtype=float, source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Define the stellar metallicity [M/H] (dex)')
# Stellar effective temperature (K)
SORBET_CDict.add('STELLAR_TEFF', value=3000, dtype=float, source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Define the stellar effective temperature (K)')
# Stellar surface gravity log g (cgs)
SORBET_CDict.add('STELLAR_LOGG', value=5.0, dtype=float, source=__NAME__,
                user=True, active=True, group=cgroup,
                description='Define the stellar surface gravity log g (cgs)')
# Debug parameter
SORBET_CDict.add('DEBUG', value=False, dtype=bool, source=__NAME__,
                 user=True, active=True, group=cgroup,
                 description='Enable debugging')

# =============================================================================
# Constants for SORBET tfit module
# =============================================================================
# set the group for all TFIT constants
group = 'TFIT'
SORBET_CDict.add_group(group, description='Configs for SORBET.TFIT: '
                                          'TFIT module',
                source=__NAME__, user=True, active=True)

# Debug parameter
SORBET_CDict.add('DEBUG', value=False, dtype=bool, source=__NAME__,
                 user=True, active=True, description='Enable debugging',
                 group=cgroup)


# =============================================================================
# Constants for SORBET RV module
# =============================================================================
# set the group for all RV constants
group = 'RV'
SORBET_CDict.add_group(group, description='Configs for SORBET.RV',
                       source=__NAME__, user=True, active=True)

# Debug parameter
SORBET_CDict.add('DEBUG', value=False, dtype=bool, source=__NAME__,
             user=True, active=True, group=cgroup,
             description='Enable debugging')


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
