# STEP_SUFFIX Complete Reference & Sources

## Summary

All 37 STEP_SUFFIX entries have been populated from the JWST pipeline source files. This document provides the mapping between our step constants and their JWST pipeline equivalents.

## JWST Pipeline Architecture

The JWST pipeline is organized in levels:

### Level 1: Detector1 Pipeline (`calwebb_detector1.py`)
Raw exposure data → Slope images (2D rate products)
- **20 steps** defined in our constants

### Level 2: Image Processing (`calwebb_image2.py`) 
2D rate products → Calibrated science images
- **6 steps** used by imaging modes

### Level 2: Spectroscopic Processing (`calwebb_spec2.py`)
2D rate products → 1D spectra
- **9 steps** used by spectroscopic modes

### Instrument-Specific
Special processing for particular instruments
- **2 steps** for unique instrument requirements

## STEP_SUFFIX Reference Table

| # | Step Constant | JWST Class | Suffix | Pipeline | Source File |
|---|---|---|---|---|---|
| 1 | GROUP_SCALE_STEP | GroupScaleStep | `_groupscalestep.fits` | detector1 | `jwst/group_scale/group_scale_step.py` |
| 2 | DQ_INIT_STEP | DQInitStep | `_dqinitstep.fits` | detector1 | `jwst/dq_init/dq_init_step.py` |
| 3 | EMICORR_STEP | EmiCorrStep | `_emicorrstep.fits` | detector1 | `jwst/emicorr/emicorr_step.py` |
| 4 | SATURATION_STEP | SaturationStep | `_saturationstep.fits` | detector1 | `jwst/saturation/saturation_step.py` |
| 5 | APPLY_INTERPIXEL_CAPACITANCE | IPCStep | `_ipcstep.fits` | detector1 | `jwst/ipc/ipc_step.py` |
| 6 | SUBTRACT_SUPERBIAS | SuperBiasStep | `_superbiasstep.fits` | detector1 | `jwst/superbias/superbias_step.py` |
| 7 | APPLY_REFERENCE_PIXEL_CORRECTION | RefPixStep | `_refpixstep.fits` | detector1 | `jwst/refpix/refpix_step.py` |
| 8 | APPLY_RSCD_CORRECTION | RscdStep | `_rscdstep.fits` | detector1 | `jwst/rscd/rscd_step.py` |
| 9 | REMOVE_FIRST_FRAME_SIGNAL | FirstFrameStep | `_firstframestep.fits` | detector1 | `jwst/firstframe/firstframe_step.py` |
| 10 | REMOVE_LAST_FRAME_SIGNAL | LastFrameStep | `_lastframestep.fits` | detector1 | `jwst/lastframe/lastframe_step.py` |
| 11 | APPLY_LINEARITY_CORRECTION | LinearityStep | `_linearitystep.fits` | detector1 | `jwst/linearity/linearity_step.py` |
| 12 | SUBTRACT_DARK_CURRENT | DarkCurrentStep | `_darkcurrentstep.fits` | detector1 | `jwst/dark_current/dark_current_step.py` |
| 13 | CORRECT_RESET_ANOMALY | ResetStep | `_resetstep.fits` | detector1 | `jwst/reset/reset_step.py` |
| 14 | CORRECT_PERSISTENCE | PersistenceStep | `_persistencestep.fits` | detector1 | `jwst/persistence/persistence_step.py` |
| 15 | CORRECT_CHARGE_MIGRATION | ChargeMigrationStep | `_chargemigrationstep.fits` | detector1 | `jwst/charge_migration/charge_migration_step.py` |
| 16 | DETECT_AND_FLAG_JUMPS | JumpStep | `_jump.fits` | detector1 | `jwst/jump/jump_step.py` |
| 17 | PICTURE_FRAME_STEP | PictureFrameStep | `_pictureframestep.fits` | detector1 | `jwst/picture_frame/picture_frame_step.py` |
| 18 | REMOVE_FLICKER_NOISE | CleanFlickerNoiseStep | `_cleanflickernoisestep.fits` | detector1 | `jwst/clean_flicker_noise/clean_flicker_noise_step.py` |
| 19 | FIT_SIGNAL_RAMPS | RampFitStep | `_rampfitstep.fits` | detector1 | `jwst/ramp_fitting/ramp_fit_step.py` |
| 20 | APPLY_GAIN_SCALING | GainScaleStep | `_gainscalestep.fits` | detector1 | `jwst/gain_scale/gain_scale_step.py` |
| 21 | SUBTRACT_BACKGROUND | BackgroundStep | `_backgroundstep.fits` | image2 | `jwst/background/background_step.py` |
| 22 | ASSIGN_WCS_SOLUTION | AssignWcsStep | `_assignwcsstep.fits` | image2/spec2 | `jwst/assign_wcs/assign_wcs_step.py` |
| 23 | EXTRACT_2D_SPECTRUM | Extract2dStep | `_extract2dstep.fits` | spec2 | `jwst/extract_2d/extract_2d_step.py` |
| 24 | EXTRACT_1D_SPECTRUM | Extract1dStep | `_extract1dstep.fits` | spec2 | `jwst/extract_1d/extract_1d_step.py` |
| 25 | SRCTYPE_DETERMINATION | SourceTypeStep | `_srctypestep.fits` | spec2 | `jwst/srctype/srctype_step.py` |
| 26 | CORRECT_STRAY_LIGHT | StraylightStep | `_straylightstep.fits` | spec2 | `jwst/straylight/straylight_step.py` |
| 27 | APPLY_FLAT_FIELD | FlatFieldStep | `_flatfieldstep.fits` | image2/spec2 | `jwst/flatfield/flatfield_step.py` |
| 28 | CORRECT_FRINGE | FringeStep | `_fringestep.fits` | spec2 | `jwst/fringe/fringe_step.py` |
| 29 | CORRECT_PATH_LOSS | PathLossStep | `_pathlossstep.fits` | spec2 | `jwst/pathloss/pathloss_step.py` |
| 30 | CORRECT_BAR_SHADOW | BarShadowStep | `_barshadowstep.fits` | spec2 | `jwst/barshadow/barshadow_step.py` |
| 31 | CORRECT_WFSS_CONTAMINATION | WfssContamStep | `_wfsscontamstep.fits` | spec2 | `jwst/wfss_contam/wfss_contam_step.py` |
| 32 | CORRECT_WAVELENGTH | WavecorrStep | `_wavecorrstep.fits` | spec2 | `jwst/wavecorr/wavecorr_step.py` |
| 33 | SUBTRACT_MASTER_BACKGROUND | MasterBackgroundStep | `_masterbackgroundstep.fits` | spec2 | `jwst/master_background/master_background_step.py` |
| 34 | MEASURE_TARGET_CENTROID | TargCentroidStep | `_targcentroidstep.fits` | special | `jwst/targ_centroid/targ_centroid_step.py` |
| 35 | CORRECT_RESIDUAL_FRINGE | ResidualFringeStep | `_residualfringestep.fits` | special | `jwst/residual_fringe/residual_fringe_step.py` |
| 36 | APPLY_PHOTOMETRIC_CALIBRATION | PhotomStep | `_photomstep.fits` | image2 | `jwst/photom/photom_step.py` |
| 37 | RESAMPLE_IMAGES | ResampleStep | `_resamplestep.fits` | image2 | `jwst/resample/resample_step.py` |

## Key Points

### Suffix Naming Convention
- JWST uses the step's `class_alias` attribute to determine output filenames
- Format: `_<class_alias>step.fits` for most steps
- Exception: JumpStep uses `_jump.fits` (shorter conventional name)

### Step Organization by Pipeline Level

**Detector1 (20 steps):** Raw data → 2D slope images
```
group_scale, dq_init, emicorr, saturation, ipc, superbias, refpix, rscd,
firstframe, lastframe, linearity, dark_current, reset, persistence,
charge_migration, jump, picture_frame, clean_flicker_noise, ramp_fit, gain_scale
```

**Image2 (6 steps):** Imaging pipeline
```
background, assign_wcs, extract_2d, flatfield, photom, resample
```

**Spec2 (9 steps):** Spectroscopic pipeline
```
assign_wcs, extract_2d, extract_1d, srctype, straylight, flatfield,
fringe, pathloss, barshadow, wfss_contam, wavecorr, master_background
```

**Instrument-Specific (2 steps):**
```
targ_centroid (TargCentroidStep), residual_fringe (ResidualFringeStep)
```

## Integration Notes

1. **File Skipping:** The `skip_step()` method in `default.py` uses these suffixes to detect if a step's output files exist
2. **Continuation:** When reprocessing, files with these suffixes are found and processing resumes from the next step
3. **Completeness:** All 37 steps now have valid suffixes for proper step skipping functionality
4. **Sources:** All names come directly from the official JWST pipeline repository at `/scratch3/jwst/jwst-pipeline`

## References

- **JWST Pipeline Repository:** `/scratch3/jwst/jwst-pipeline`
- **Official Steps:** Each step is in its own directory under `jwst/`
- **Pipeline Definitions:**
  - Level 1: `jwst/pipeline/calwebb_detector1.py`
  - Level 2 Image: `jwst/pipeline/calwebb_image2.py`
  - Level 2 Spec: `jwst/pipeline/calwebb_spec2.py`
