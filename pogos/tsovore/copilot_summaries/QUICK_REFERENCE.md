JWST Benchmark Implementation - Quick Reference
==================


This file provides a quick reference to all available benchmark implementations
and their usage.

AVAILABLE CLASSES:
==================

NIRISS (niriss.py):
-------------------
from pogos.tsovore.instruments.niriss import NirissSoss, NirissSossSuperstripe

NirissSoss:
  - Instrument: JWST.NIRISS.SOSS
  - Observation Type: Time-series spectroscopy
  - Exp Type: NIS_SOSS
  - Pipelines: calwebb_detector1 → calwebb_spec2
  - Use Case: NIRISS SOSS observations

NirissSossSuperstripe:
  - Instrument: JWST.NIRISS.SOSS.SUPERSTRIPE
  - Observation Type: Extended time-series spectroscopy
  - Exp Type: NIS_SOSS (superstripe mode)
  - Pipelines: calwebb_detector1 → calwebb_spec2
  - Use Case: Long-duration NIRISS SOSS observations with improved background

NIRCam (nircam.py):
-------------------
from pogos.tsovore.instruments.nircam import NircamImaging, NircamGrism, NircamMultistripe

NircamImaging:
  - Instrument: JWST.NIRCAM.IMAGING
  - Observation Type: Direct imaging
  - Exp Type: NRC_IMAGE
  - Pipelines: calwebb_detector1 → calwebb_image2
  - Use Case: NIRCam direct imaging observations

NircamGrism:
  - Instrument: JWST.NIRCAM.GRISM
  - Observation Type: Grism slitless spectroscopy
  - Exp Type: NRC_WFSS, NRC_GRISM
  - Pipelines: calwebb_detector1 → calwebb_spec2 (grism)
  - Use Case: NIRCam grism/WFSS observations

NircamMultistripe:
  - Instrument: JWST.NIRCAM.MULTISTRIPE
  - Observation Type: Multi-channel spectroscopy
  - Exp Type: NRC_MULTISTRIPE
  - Pipelines: calwebb_detector1 → calwebb_spec2 (grism-like)
  - Use Case: NIRCam multistripe spectroscopic observations

NIRSpec (nirspec.py):
---------------------
from pogos.tsovore.instruments.nirspec import NirspecBotsPrism, NirspecBotsMedium, NirspecBotsHigh

NirspecBotsPrism:
  - Instrument: JWST.NIRSPEC.BOTS.PRISM
  - Observation Type: Bright Object Time Series (prism)
  - Exp Type: NRS_PRISM
  - Pipelines: calwebb_detector1 → calwebb_spec2 (slits)
  - Use Case: NIRSpec BOTS observations with prism

NirspecBotsMedium:
  - Instrument: JWST.NIRSPEC.BOTS.MEDIUM
  - Observation Type: Bright Object Time Series (medium grating)
  - Exp Type: NRS_MEDIUM_MEDIUM
  - Pipelines: calwebb_detector1 → calwebb_spec2 (slits)
  - Use Case: NIRSpec BOTS observations with medium grating

NirspecBotsHigh:
  - Instrument: JWST.NIRSPEC.BOTS.HIGH
  - Observation Type: Bright Object Time Series (high grating)
  - Exp Type: NRS_HIGH_HIGH
  - Pipelines: calwebb_detector1 → calwebb_spec2 (slits)
  - Use Case: NIRSpec BOTS observations with high grating

MIRI (miri2.py):
----------------
from pogos.tsovore.instruments.miri2 import MiriImaging, MiriLrs

MiriImaging:
  - Instrument: JWST.MIRI.IMAGING
  - Observation Type: Direct imaging
  - Exp Type: MIR_IMAGE
  - Pipelines: calwebb_detector1 → calwebb_image2
  - Use Case: MIRI direct imaging observations

MiriLrs:
  - Instrument: JWST.MIRI.LRS
  - Observation Type: Low resolution spectroscopy
  - Exp Type: MIR_LRS-FIXEDSLIT, MIR_LRS-SLITLESS
  - Pipelines: calwebb_detector1 → calwebb_spec2 (common)
  - Use Case: MIRI LRS spectroscopic observations

BASIC USAGE PATTERN:
====================

1. Import the desired class:
   from pogos.tsovore.instruments.niriss import NirissSoss

2. Create an instance with parameters:
   params = {...}  # Your configuration parameters
   processor = NirissSoss(params)

3. Run the full pipeline:
   processor.process()

4. Output files will be saved with appropriate suffixes:
   - Level 1: _rate.fits, _rateints.fits
   - Level 2: _cal.fits, _x1d.fits (for spectroscopy), etc.

LEVEL 1 PROCESSING STEPS:
=========================

Applied to ALL instruments in this order:

1. group_scale_step() - Scale group data
2. dq_init_step() - Initialize data quality flags
3. saturation_step() - Flag saturated pixels
4. apply_interpixel_capacitance() - Correct for IPC
5. subtract_superbias() [NIR] / emicorr_step() [MIRI] - Dark reference
6. apply_reference_pixel_correction() - Reference pixel correction
7. apply_linearity_correction() - Linearity correction
8. subtract_dark_current() - Dark current subtraction
9. correct_charge_migration() - Charge migration correction
10. detect_and_flag_jumps() - Cosmic ray detection
11. picture_frame_step() [optional] - Picture frame correction
12. remove_flicker_noise() - 1/f noise removal
13. fit_signal_ramps() - Produce rate products (returns: rate_data, ints_model)
14. apply_gain_scaling() - Gain scaling (applied twice: to rate and ints_model)

LEVEL 2 PROCESSING - IMAGING (calwebb_image2):
===============================================

Applied to: NircamImaging, MiriImaging

1. subtract_background() - Background subtraction
2. assign_wcs_solution() - WCS assignment
3. apply_flat_field() - Flat field correction
4. apply_photometric_calibration() - Photometric calibration
5. resample_images() [optional] - Resample to common grid

LEVEL 2 PROCESSING - SPECTROSCOPY (calwebb_spec2):
==================================================

NIRISS SOSS specific order:
1. assign_wcs_solution() - WCS assignment
2. remove_flicker_noise() - 1/f correction (may be skipped)
3. srctype_determination() - Source type determination
4. apply_flat_field() - Flat field correction
5. correct_stray_light() - Stray light removal
6. correct_fringe() - Fringe correction
7. correct_path_loss() - Path loss correction
8. correct_bar_shadow() - Bar shadow correction
9. extract_1d_spectrum() - 1D spectrum extraction
10. apply_photometric_calibration() - Photometric calibration

NIRCam Grism specific order:
1. assign_wcs_solution() - WCS assignment
2. apply_flat_field() - Flat field (before extract_2d!)
3. extract_2d_spectrum() - 2D spectrum extraction
4. srctype_determination() - Source type determination
5. correct_stray_light() - Stray light removal
6. correct_fringe() - Fringe correction
7. correct_path_loss() - Path loss correction
8. correct_bar_shadow() - Bar shadow correction
9. correct_wfss_contamination() - WFSS contamination
10. apply_photometric_calibration() - Photometric calibration

NIRSpec BOTS specific order:
1. assign_wcs_solution() - WCS assignment
2. extract_2d_spectrum() - 2D spectrum extraction
3. srctype_determination() - Source type determination
4. subtract_master_background() - Master background subtraction
5. correct_wavelength() - Wavelength correction
6. apply_flat_field() - Flat field correction
7. correct_path_loss() - Path loss correction
8. correct_bar_shadow() - Bar shadow correction
9. apply_photometric_calibration() - Photometric calibration
10. extract_1d_spectrum() - 1D spectrum extraction

MIRI LRS specific order:
1. assign_wcs_solution() - WCS assignment
2. srctype_determination() - Source type determination
3. correct_stray_light() - Stray light removal
4. apply_flat_field() - Flat field correction
5. correct_fringe() - Fringe correction
6. [skip path_loss - NOT applied to MIR_LRS]
7. correct_bar_shadow() - Bar shadow correction
8. apply_photometric_calibration() - Photometric calibration
9. correct_residual_fringe() - Residual fringe correction (MIRI-specific)
10. extract_1d_spectrum() - 1D spectrum extraction

BENCHMARKING TIPS:
==================

1. Compare step-by-step outputs against official JWST pipelines
2. Monitor execution time for each step
3. Check for differences in output product quality
4. Validate intermediate products at critical steps:
   - After Level 1: _rate.fits
   - After Level 2: _cal.fits (imaging) or _x1d.fits (spectroscopy)

5. Instrument-specific checks:
   - NIRISS SOSS: Verify time-series quality and time correlation preservation
   - NIRCam Imaging: Check for flat field artifacts and edge effects
   - NIRCam Grism: Verify spectral trace alignment and contamination flags
   - NIRSpec BOTS: Check wavelength solution accuracy
   - MIRI Imaging: Verify thermal background subtraction
   - MIRI LRS: Check for fringing artifacts

MODIFICATIONS FOR CUSTOM PROCESSING:
====================================

If you need to modify the processing:

1. Individual steps can be skipped by commenting them out
2. Processing order can be changed by rearranging method calls
3. Custom parameters can be passed to individual steps
4. New steps can be inserted between existing steps

Example: Skip flat field correction
def process(self):
    # ... Level 1 processing ...
    # rate_data = self.apply_flat_field()  # Commented out
    rate_data = self.correct_stray_light()  # Next step
    # ... rest of processing ...

REFERENCES:
===========

JWST Pipeline Documentation:
https://jwst-pipeline.readthedocs.io/en/latest/

JWST Data Processing:
https://jwst-docs.stsci.edu/jwst-calibration-pipeline-overview

Created: 2025-01-16
"""
