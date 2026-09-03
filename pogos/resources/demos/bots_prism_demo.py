#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# CODE NAME HERE

# CODE DESCRIPTION HERE

Created on 2025-03-25 at 09:57

@author: cook
"""


import pogos.core.base as pogos_base
from pogos.resources.demos import demos
from sossisse.core import constants as sconst
from pogos.constants import constants as pconst

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'bots_prism_demo.py'

# =============================================================================
# Define demo classes
# =============================================================================
class BotsPrismDemo_WASP39b(demos.PogoDemo):
    classname = 'BotsPrismDemo_WASP39b'
    object = 'WASP 39b'
    keywords = ['transit']
    instrument = 'JWST.NIRSPEC.BOTS.PRISM'
    description = 'WASP 39b transit observed on 2022-07-10'
    date = '2025-03-25'
    author = 'Neil Cook'

    def __init__(self):
        self.title = 'JWST.NIRSPEC.BOTS.PRISM WASP 39b transit [{tflavours}]'
        # in form DEMO_{OBJNAME}.{date}.{telescope}.{inst}.{mode}.{flavours}
        self.id = 'DEMO_WASP39b.20220710.JWST.NIRSPEC.BOTS.PRISM.{tflavours}'
        # define the flavours selected by the user
        self.flavours = []
        # define the string flavours (shortened versions of flavours for
        #  title and id)
        self.tflavours = []
        # url for data download
        self.url = 'http://206.12.93.77/ari/data/pogos/demos/nirspec/'
        self.download = dict()
        self.redsteps = dict()

        # define the reduction steps (and methods to be run) if these steps
        # are being run
        self.redsteps['Extraction:SOSSISSE'] = [self.sossisse]
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

        # Instrument mode i.e. JWST.NIRISS.SOSS or JWST.NIRSPEC.BOTS.PRISM
        self.cdict.set('INSTRUMENTMODE', group=cgroup, source=__NAME__,
                       value=self.instrument)
        # =====================================================================
        # Turn all modes off by default
        # =====================================================================
        for submodule in pogos_base.SUBMODULES:
            self.cdict.set(submodule, group='RUN', source=__NAME__,
                           value=False)

    # TODO: Add tsovore
    def tsovore(self):
        raise NotImplemented()

    def sossisse(self):
        # Add the sub-constants-dictionary for SOSSISSE
        SOSSISSE_CDict = sconst.CDict.copy(source=__NAME__)
        self.cdict.add_sub_cdict('SOSSISSE', SOSSISSE_CDict, source=__NAME__)
        # =====================================================================
        # Add to the downloads
        # =====================================================================
        self.download['SOSSISSE.GENERAL.FILES'] = 'SOSSISSE.PATHS.RAWPATH'
        self.download['SOSSISSE.GENERAL.WAVE_FILE'] = 'SOSSISSE.PATHS.CALIBPATH'

        # =====================================================================
        # Switches to turn of major features
        # =====================================================================
        cgroup = 'RUN'
        # Run SOSSISSE
        self.cdict.set('SOSSISSE', group=cgroup, source=__NAME__, value=True)
        # =====================================================================
        # Switches to turn large parts of the code on/off
        # =====================================================================
        cgroup = 'SOSSISSE.RUN'

        # Switch for turning on/off the linear reconstruction step
        self.cdict.set('LINEAR_RECON', group=cgroup, source=__NAME__,
                       value=True)

        # Switch for turning on/off the spectral extraction
        self.cdict.set('SPECTRAL_EXTRACTION', group=cgroup, source=__NAME__,
                       value=True)

        # =====================================================================
        # Definition of inputs related to the data
        # =====================================================================
        cgroup = 'SOSSISSE.INPUTS'

        # The sub-directory to use for this SOSSISSE run.
        # This should be descriptive and unique.
        # It should contain no whitespaces or special
        # characters other than underscoes
        # All sossisse data will be stored in
        #      {GLOBAL.DATA_PATH}/sossisse/{SUBDIRECTORY}/
        self.cdict.set('SUBDIRECTORY', group=cgroup, source=__NAME__,
                       value=self.get_prop('id'))

        # Description of the SOSSISSE run e.g. object name, date of observation,
        # is it a transit or an eclipse etc.
        self.cdict.set('DESCRIPTION', group=cgroup, source=__NAME__,
                       value=self.description)

        # Instrument mode
        self.cdict.set('INSTRUMENTMODE', group=cgroup, source=__NAME__,
                       value=self.instrument)

        # Name of the object (must match the object directory name)
        self.cdict.set('OBJECTNAME', group=cgroup, source=__NAME__,
                       value='WASP39b')

        # =====================================================================
        # Definition of general inputs
        # =====================================================================
        cgroup = 'SOSSISSE.GENERAL'

        # List of files to be processed in form:
        # FILES:
        #  - file1
        #  - file2
        #  - file3
        files = ['jw01366004001_04101_00001-seg001_nrs1_rateints.fits',
                 'jw01366004001_04101_00001-seg002_nrs1_rateints.fits',
                 'jw01366004001_04101_00001-seg003_nrs1_rateints.fits',
                 'jw01366004001_04101_00001-seg004_nrs1_rateints.fits']
        self.cdict.set('FILES', group=cgroup, source=__NAME__, value=files)

        # do background correction - must have BKGFILE defined to do this
        self.cdict.set('DO_BACKGROUND', value=False, group=cgroup,
                       source=__NAME__)

        # flat field file --> leave as '' if there is no flat field available
        #     for the mode
        self.cdict.set('FLATFILE', group=cgroup, source=__NAME__,
                       value=None)

        # trace position file
        self.cdict.set('POS_FILE', group=cgroup, source=__NAME__,
                       value=None)

        # Wavelength calibration file
        wavefile = 'jw01366004001_04101_00001-seg004_nrs1_x1dints.fits'
        self.cdict.set('WAVE_FILE', group=cgroup, source=__NAME__,
                       value=wavefile)

        # Wavelength calibration file type
        self.cdict.set('WAVE_FILE_TYPE', group=cgroup, source=__NAME__,
                       value='ext1d')

        # Define which orders to use e.g.
        # - 1
        # - 2
        self.cdict.set('TRACE_ORDERS', group=cgroup, source=__NAME__,
                       value=None)

        # =====================================================================
        # Definition of inputs related to the position within data cube timeseries
        # =====================================================================
        cgroup = 'SOSSISSE.WLC.INPUTS'

        # Integrations used to construct a model PSF.
        #     This should be a list of [start, end] lists
        #     These should be out-of-transit (if any) and without flares.
        #     If you observed constantly a variable object (brown dwarf, phase curve),
        #     you should enter the first to last as frame IDs, except significant
        #     flares.
        #     Note that on a first pass of data reduction, you may not know the
        #     optimal parameters. You can enter a guess and fine-tune in a second step.
        #     As a starting point, BASELINE_INTS can be [0, NINTS-1] where NINTS can
        #     be found in your fits header.
        #     Note the 1st frame is zero (pythonic numbering)
        #     Note that leaving this blank sets the baseline from 0 to NINTS-1
        #     E.g.
        #         BASELINE_INTS:
        #               - [0, 89]
        #               - [111, 153]
        self.cdict.set('BASELINE_INTS', group=cgroup, source=__NAME__,
                       value=[[0, 8199], [15700, 21500]])

        # =====================================================================
        # Definition of inputs related to handling of the data within each frame
        # =====================================================================
        cgroup = 'SOSSISSE.WLC.GENERAL'

        # Trace extraction width. Set to 0 to use the full image
        self.cdict.set('LINRECON_TRACE_WIDTH', group=cgroup, source=__NAME__,
                       value=40)

        # define the width for masking the white light curve trace
        #         Default
        self.cdict.set('TRACE_WIDTH_MASKING', group=cgroup, source=__NAME__,
                       value=40)
        # Set the range of dys to scan over number of -nbypix/trace_y_scale to
        #     +nbyix/trace_y_scale
        self.cdict.set('TRACE_Y_SCALE', group=cgroup, source=__NAME__,
                       value=10)
        # Set the range of dys to scan over number of -nbxpix/trace_x_scale to
        #     +nbxpix/trace_x_scale
        self.cdict.set('TRACE_X_SCALE', group=cgroup, source=__NAME__,
                       value=10)

    # TODO: Add sorbet
    def sorbet(self):
        raise NotImplemented()

    # TODO: Add sorbet wlca
    def sorbet_wlca(self):
        raise NotImplemented()

    # TODO: Add sorbet wlca
    def sorbet_slca(self):
        raise NotImplemented()


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

