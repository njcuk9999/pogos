#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-03-25 at 09:57

@author: cook
"""


from pogos.core import definitions
from pogos.resources.demos import demos
from pogos.constants import constants as pconst
from pogos.constants import miriam as mconst
from pogos.constants import tsovore as tconst
from pogos.constants import sorbet as sbconst

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'miri_demos.py'

# =============================================================================
# Define demo classes
# =============================================================================
class MiriImagingDemo_LHS1140(demos.PogoDemo):
    classname = 'MiriImagingDemo_LHS1140'
    object = 'LHS-1140'
    keywords = ['eclipse']
    instrument = 'JWST.MIRI.IMAGING'
    description = 'LHS-1140 eclipse observed on 2024-07-07'
    date = '2025-10-16'
    author = 'Etienne Artigau'

    def __init__(self):
        self.title = 'JWST.MIRI.IMAGING LHS-1140 eclipse [{tflavours}]'
        # in form DEMO_{OBJNAME}.{date}.{telescope}.{inst}.{mode}.{flavours}
        self.id = 'DEMO_LHS1140.20240707.JWST.MIRI.IM.{tflavours}'
        # define the flavours selected by the user
        self.flavours = []
        # define the string flavours (shortened versions of flavours for
        #  title and id)
        self.tflavours = []
        # url for data download
        self.url = 'http://206.12.93.77/ari/data/pogos/demos/miri/'
        self.download = dict()
        self.redsteps = dict()

        # define the reduction steps (and methods to be run) if these steps
        # are being run
        self.redsteps['Pre-extraction:TSOVORE'] = [self.tsovore]
        self.redsteps['Extraction:MIRIAM'] = [self.miriam]
        self.redsteps['Post-extraction:SORBET.WLCA'] = [self.sorbet,
                                                        self.sorbet_wlca]
        # start cdict as a copy of the main POGOS constants dictionary
        self.cdict = pconst.CDict.copy(source=__NAME__)
        # the startup method fills the cdict with the global settings
        # and sets default values
        self.startup()

    def startup(self):
        # =====================================================================
        # global settings (generally don't touch these)
        # =====================================================================
        cgroup = 'GLOBAL'

        # Instrument mode i.e. JWST.NIRISS.SOSS or JWST.NIRISS.PRISM
        self.cdict.set('INSTRUMENTMODE', group=cgroup, source=__NAME__,
                       value=self.instrument)
        # =====================================================================
        # Turn all modes off by default
        # =====================================================================
        for step in definitions.RED_STEPS:
            self.cdict.set(step.name, group='RUN', source=__NAME__,
                           value=False)

    def tsovore(self):
        # Add the sub-constants-dictionary for TSOVORE
        TSOvore_CDict = tconst.TSOVORE_CDict.copy(source=__NAME__)
        self.cdict.add_sub_cdict('TSOVORE', TSOvore_CDict, source=__NAME__)
        # =====================================================================
        # Add to the downloads
        # =====================================================================
        self.download['TSOVORE.INPUTS.FILES'] = 'TSOVORE.PATHS.INPUT_PATH'

        # =====================================================================
        # Switches to turn of major features
        # =====================================================================
        cgroup = 'RUN'
        # Run TSOVORE
        self.cdict.set('TSOVORE', group=cgroup, source=__NAME__, value=True)
        # =====================================================================
        # General settings
        # =====================================================================
        cgroup = 'TSOVORE.GENERAL'

        # The sub-directory to use for this TSOVORE run.
        # This should be descriptive and unique.
        # It should contain no whitespaces or special
        # characters other than underscoes
        # All tsovore data will be stored in
        #      {GLOBAL.DATA_PATH}/tsovore/{SUBDIRECTORY}/
        self.cdict.set('SUBDIRECTORY', group=cgroup, source=__NAME__,
                       value=self.get_prop('id'))

        # Description of the TSOVORE run e.g. object name, date of observation,
        # is it a transit or an eclipse etc.
        self.cdict.set('DESCRIPTION', group=cgroup, source=__NAME__,
                       value=self.description)

        # =====================================================================
        # Input settings
        # =====================================================================
        cgroup = 'TSOVORE.INPUTS'

        # Instrument mode i.e. JWST.NIRISS.SOSS or JWST.NIRISS.PRISM
        self.cdict.set('INSTRUMENTMODE', group=cgroup, source=__NAME__,
                       value='JWST.MIRI.IMAGING')

        # List of files to be processed in form:
        # FILES:
        #  - file1
        #  - file2
        #  - file3
        files = ['jw03730009001_03101_00001-seg001_mirimage_uncal.fits',
                 'jw03730009001_03101_00001-seg002_mirimage_uncal.fits',
                 'jw03730009001_03101_00001-seg003_mirimage_uncal.fits',
                 'jw03730009001_03101_00001-seg004_mirimage_uncal.fits',
                 'jw03730009001_03101_00001-seg005_mirimage_uncal.fits']
        self.cdict.set('FILES', group=cgroup, source=__NAME__, value=files)

        # Whether to remove intermediate files
        self.cdict.set('REMOVE_INTERMEDIATES', group=cgroup, source=__NAME__,
                  value=True)

    def miriam(self):
        # Add the sub-constants-dictionary for MIRIAM
        MIRIAM_CDict = mconst.MIRIAM_CDict.copy(source=__NAME__)
        self.cdict.add_sub_cdict('MIRIAM', MIRIAM_CDict, source=__NAME__)
        # =====================================================================
        # Add to the downloads
        # =====================================================================
        self.download['MIRIAM.INPUTS.FILES'] = 'MIRIAM.PATHS.INPUT_PATH'

        # =====================================================================
        # Switches to turn of major features
        # =====================================================================
        cgroup = 'RUN'
        # Run TSOVORE
        self.cdict.set('MIRIAM', group=cgroup, source=__NAME__, value=True)
        # =====================================================================
        # General settings
        # =====================================================================
        cgroup = 'MIRIAM.GENERAL'

        # The sub-directory to use for this MIRIAM run.
        # This should be descriptive and unique.
        # It should contain no whitespaces or special
        # characters other than underscoes
        # All miriam data will be stored in
        # {GLOBAL.DATA_PATH}/miriam/{SUBDIRECTORY}/
        self.cdict.set('SUBDIRECTORY', group=cgroup, source=__NAME__,
                  value=self.get_prop('id'))

        # Description of the MIRIAM run e.g. object name, date of observation,
        # is it a transit or an eclipse etc.
        self.cdict.set('DESCRIPTION', group=cgroup, source=__NAME__,
                  value=self.description)

        # =====================================================================
        # Input settings
        # =====================================================================
        cgroup = 'MIRIAM.INPUTS'

        # List of files to be processed in form:
        # FILES:
        #  - file1
        #  - file2
        #  - file3
        files = ['jw03730009001_03101_00001-seg001_mirimage_rateints.fits',
                 'jw03730009001_03101_00001-seg002_mirimage_rateints.fits',
                 'jw03730009001_03101_00001-seg003_mirimage_rateints.fits',
                 'jw03730009001_03101_00001-seg004_mirimage_rateints.fits',
                 'jw03730009001_03101_00001-seg005_mirimage_rateints.fits']
        self.cdict.set('FILES', group=cgroup, source=__NAME__, value=files)

    def sorbet(self):
        # Add the sub-constants-dictionary for SORBET
        # Add the sub-constants-dictionary for MIRIAM
        SORBET_CDict = sbconst.SORBET_CDict.copy(source=__NAME__)
        self.cdict.add_sub_cdict('SORBET', SORBET_CDict, source=__NAME__)

        # =====================================================================
        # Constants for SORBET: Suite Of Reduction tools for Both Eclipse
        # and Transit
        # =====================================================================
        cgroup = 'SORBET.GENERAL'

        # The sub-directory to use for this SORBET run.
        # This should be descriptive and unique.
        # It should contain no whitespaces or special
        # characters other than underscoes
        # All sorbet data will be stored in
        # {GLOBAL.DATA_PATH}/sorbet/{SUBDIRECTORY}/
        self.cdict.set('SUBDIRECTORY', group=cgroup, source=__NAME__,
                  value=self.get_prop('id'))
        # Description of the SORBET run e.g. object name, date of observation,
        # is it a transit or an eclipse etc.
        self.cdict.set('DESCRIPTION', group=cgroup, source=__NAME__,
                  value=self.description)

    def sorbet_wlca(self):
        # =====================================================================
        # Add to the downloads
        # =====================================================================
        self.download['SORBET.WLCA.INPUT_FILE'] = 'SORBET.WLCA.INPUT_PATH'
        # =====================================================================
        # Switches to turn large parts of the code on/off
        # =====================================================================
        # Switch for turning on/off the white light curve transit fit
        self.cdict.set('SORBET.WLCA', group='RUN', source=__NAME__, value=True)

        # set the group for the rest of the constants
        cgroup = 'SORBET.WLCA'
        # =====================================================================
        # Definition of inputs related to the data
        # =====================================================================
        # Path to input file relative to GLOBAL data path defined by the user
        self.cdict.set('INPUT_FILE', group=cgroup, source=__NAME__,
                       value='white_light_curve.fits')

        # =====================================================================
        # Definition of general inputs SORBET_WLCA
        # =====================================================================
        # Prior distributions for the default juliet parameterization
        jps_values = ['P_p1', 't0_p1', 'p_p1', 'b_p1', 'a_p1',
                      'ecc_p1', 'omega_p1',
                      'q1_{INST_MODE}', 'q2_{INST_MODE}',
                      'mdilution_{INST_MODE}', 'mflux_{INST_MODE}',
                      'sigma_w_{INST_MODE}']
        self.cdict.set('JULIET_PARAMETERS', group=cgroup, source=__NAME__,
                       value=jps_values)

        # Prior distributions for the default juliet parameterization
        jpd_values = dict()
        jpd_values['P_p1'] = 'fixed'
        jpd_values['t0_p1'] = 'uniform'
        jpd_values['p_p1'] = 'uniform'
        jpd_values['b_p1'] = 'truncatednormal'
        jpd_values['a_p1'] = 'uniform'
        jpd_values['ecc_p1'] = 'fixed'
        jpd_values['omega_p1'] = 'fixed'
        jpd_values['q1_{INST_MODE}'] = 'uniform'
        jpd_values['q2_{INST_MODE}'] = 'uniform'
        jpd_values['mdilution_{INST_MODE}'] = 'fixed'
        jpd_values['mflux_{INST_MODE}'] = 'fixed'
        jpd_values['sigma_w_{INST_MODE}'] = 'loguniform'
        self.cdict.set('JULIET_PRIOR_DISTS', group=cgroup, source=__NAME__,
                       value=jpd_values)
        # Priors for the default juliet parameterization
        jpv_values = dict()
        jpv_values['P_p1'] = 3.777940
        jpv_values['t0_p1'] = [2460498.5, 2460498.8]
        jpv_values['p_p1'] = [0., 1.]
        jpv_values['b_p1'] = [0.090, 0.65, 0.0, 1.0]
        jpv_values['a_p1'] = [10, 30] # 26.57
        jpv_values['ecc_p1'] = 0.0
        jpv_values['omega_p1'] = 90.0
        jpv_values['q1_{INST_MODE}'] = [0.0, 1.0]
        jpv_values['q2_{INST_MODE}'] = [0.0, 1.0]
        jpv_values['mdilution_{INST_MODE}'] = 1.0
        jpv_values['mflux_{INST_MODE}'] = 0.0
        jpv_values['sigma_w_{INST_MODE}'] = [1, 1000]
        self.cdict.set('JULIET_PRIOR_VALS', group=cgroup, source=__NAME__,
                       value=jpv_values)


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
