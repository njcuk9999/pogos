# STEP_SUFFIX Source Reference - JWST Pipeline

This document shows where each step suffix comes from in the JWST pipeline.

## Source Files Reference

All step definitions and naming conventions come from:
- **Repository**: `/scratch3/jwst/jwst-pipeline`
- **Main Pipelines**: 
  - `jwst/pipeline/calwebb_detector1.py` - Level 1 detector processing
  - `jwst/pipeline/calwebb_image2.py` - Level 2 imaging
  - `jwst/pipeline/calwebb_spec2.py` - Level 2 spectroscopy

## STEP_SUFFIX Mapping

### Detector1 Level (calwebb_detector1.py)

These steps are from the official JWST detector1 pipeline:

```python
from jwst.group_scale import group_scale_step
from jwst.dq_init import dq_init_step
from jwst.emicorr import emicorr_step
from jwst.saturation import saturation_step
from jwst.ipc import ipc_step
from jwst.superbias import superbias_step
from jwst.refpix import refpix_step
from jwst.rscd import rscd_step
from jwst.firstframe import firstframe_step
from jwst.lastframe import lastframe_step
from jwst.linearity import linearity_step
from jwst.dark_current import dark_current_step
from jwst.reset import reset_step
from jwst.persistence import persistence_step
from jwst.charge_migration import charge_migration_step
from jwst.jump import jump_step
from jwst.picture_frame import picture_frame_step
from jwst.clean_flicker_noise import clean_flicker_noise_step
from jwst.ramp_fitting import ramp_fit_step
from jwst.gain_scale import gain_scale_step
```

| Step Constant | JWST Class | Suffix | Source |
|---|---|---|---|
| GROUP_SCALE_STEP | GroupScaleStep | `_groupscalestep.fits` | `jwst/group_scale/group_scale_step.py` |
| DQ_INIT_STEP | DQInitStep | `_dqinitstep.fits` | `jwst/dq_init/dq_init_step.py` |
| EMICORR_STEP | EmiCorrStep | `_emicorrstep.fits` | `jwst/emicorr/emicorr_step.py` |
| SATURATION_STEP | SaturationStep | `_saturationstep.fits` | `jwst/saturation/saturation_step.py` |
| APPLY_INTERPIXEL_CAPACITANCE | IPCStep | `_ipcstep.fits` | `jwst/ipc/ipc_step.py` |
| SUBTRACT_SUPERBIAS | SuperBiasStep | `_superbiasstep.fits` | `jwst/superbias/superbias_step.py` |
| APPLY_REFERENCE_PIXEL_CORRECTION | RefPixStep | `_refpixstep.fits` | `jwst/refpix/refpix_step.py` |
| APPLY_RSCD_CORRECTION | RscdStep | `_rscdstep.fits` | `jwst/rscd/rscd_step.py` |
| REMOVE_FIRST_FRAME_SIGNAL | FirstFrameStep | `_firstframestep.fits` | `jwst/firstframe/firstframe_step.py` |
| REMOVE_LAST_FRAME_SIGNAL | LastFrameStep | `_lastframestep.fits` | `jwst/lastframe/lastframe_step.py` |
| APPLY_LINEARITY_CORRECTION | LinearityStep | `_linearitystep.fits` | `jwst/linearity/linearity_step.py` |
| SUBTRACT_DARK_CURRENT | DarkCurrentStep | `_darkcurrentstep.fits` | `jwst/dark_current/dark_current_step.py` |
| CORRECT_RESET_ANOMALY | ResetStep | `_resetstep.fits` | `jwst/reset/reset_step.py` |
| CORRECT_PERSISTENCE | PersistenceStep | `_persistencestep.fits` | `jwst/persistence/persistence_step.py` |
| CORRECT_CHARGE_MIGRATION | ChargeMigrationStep | `_chargemigrationstep.fits` | `jwst/charge_migration/charge_migration_step.py` |
| DETECT_AND_FLAG_JUMPS | JumpStep | `_jump.fits` | `jwst/jump/jump_step.py` |
| PICTURE_FRAME_STEP | PictureFrameStep | `_pictureframestep.fits` | `jwst/picture_frame/picture_frame_step.py` |
| REMOVE_FLICKER_NOISE | CleanFlickerNoiseStep | `_cleanflickernoisestep.fits` | `jwst/clean_flicker_noise/clean_flicker_noise_step.py` |
| FIT_SIGNAL_RAMPS | RampFitStep | `_rampfitstep.fits` | `jwst/ramp_fitting/ramp_fit_step.py` |
| APPLY_GAIN_SCALING | GainScaleStep | `_gainscalestep.fits` | `jwst/gain_scale/gain_scale_step.py` |

### Image2 Level (calwebb_image2.py)

These steps are used in the image processing pipeline (Level 2):

| Step Constant | JWST Class | Suffix | Source |
|---|---|---|---|
| SUBTRACT_BACKGROUND | BackgroundStep | `_backgroundstep.fits` | `jwst/background/background_step.py` |
| ASSIGN_WCS_SOLUTION | AssignWcsStep | `_assignwcsstep.fits` | `jwst/assign_wcs/assign_wcs_step.py` |
| EXTRACT_2D_SPECTRUM | Extract2dStep | `_extract2dstep.fits` | `jwst/extract_2d/extract_2d_step.py` |
| APPLY_FLAT_FIELD | FlatFieldStep | `_flatfieldstep.fits` | `jwst/flatfield/flatfield_step.py` |
| APPLY_PHOTOMETRIC_CALIBRATION | PhotomStep | `_photomstep.fits` | `jwst/photom/photom_step.py` |
| RESAMPLE_IMAGES | ResampleStep | `_resamplestep.fits` | `jwst/resample/resample_step.py` |

### Spec2 Level (calwebb_spec2.py)

These steps are used in the spectroscopy processing pipeline (Level 2):

| Step Constant | JWST Class | Suffix | Source |
|---|---|---|---|
| EXTRACT_1D_SPECTRUM | Extract1dStep | `_extract1dstep.fits` | `jwst/extract_1d/extract_1d_step.py` |
| SRCTYPE_DETERMINATION | SourceTypeStep | `_srctypestep.fits` | `jwst/srctype/srctype_step.py` |
| CORRECT_STRAY_LIGHT | StraylightStep | `_straylightstep.fits` | `jwst/straylight/straylight_step.py` |
| CORRECT_FRINGE | FringeStep | `_fringestep.fits` | `jwst/fringe/fringe_step.py` |
| CORRECT_PATH_LOSS | PathLossStep | `_pathlossstep.fits` | `jwst/pathloss/pathloss_step.py` |
| CORRECT_BAR_SHADOW | BarShadowStep | `_barshadowstep.fits` | `jwst/barshadow/barshadow_step.py` |
| CORRECT_WFSS_CONTAMINATION | WfssContamStep | `_wfsscontamstep.fits` | `jwst/wfss_contam/wfss_contam_step.py` |
| CORRECT_WAVELENGTH | WavecorrStep | `_wavecorrstep.fits` | `jwst/wavecorr/wavecorr_step.py` |
| SUBTRACT_MASTER_BACKGROUND | MasterBackgroundStep | `_masterbackgroundstep.fits` | `jwst/master_background/master_background_step.py` |

### Instrument-Specific Steps

These steps are used by specific instruments:

| Step Constant | JWST Class | Suffix | Source |
|---|---|---|---|
| MEASURE_TARGET_CENTROID | TargCentroidStep | `_targcentroidstep.fits` | `jwst/targ_centroid/targ_centroid_step.py` |
| CORRECT_RESIDUAL_FRINGE | ResidualFringeStep | `_residualfringestep.fits` | `jwst/residual_fringe/residual_fringe_step.py` |

## Naming Convention

The JWST stpipe framework automatically generates output filenames based on:
1. Each step class's `class_alias` attribute
2. Appending `step.fits` to the alias name
3. Example: `class_alias = "group_scale"` → `_groupscalestep.fits`

## STEP_SUFFIX Completeness

✅ **All 37 steps now have defined suffixes:**
- 20 Detector1 steps
- 6 Image2-specific steps
- 9 Spec2-specific steps
- 2 Instrument-specific steps

The suffixes are used by the `skip_step()` function in `default.py` to determine if a step's output files already exist, allowing for efficient processing continuation.

