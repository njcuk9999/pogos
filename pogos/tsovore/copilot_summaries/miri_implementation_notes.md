# MIRI Implementation Notes

## Key Design Decisions in Current miri.py

### 1. EXPANDED INDIVIDUAL DETECTOR INIT STEPS
Current Implementation:
- Calls: `group_scale_step()`, `dq_init_step()`, `emicorr_step()`, `saturation_step()`
- This matches the official JWST pipeline granularity exactly

Previous Alternative:
- Used bundled `initialize_detector_data()` method
- Combined steps 1.1-1.4 into a single call

### 2. EXPLICIT STEP ORDERING
Current Implementation:
- Each step is called individually with clear comments
- Makes the exact processing sequence visible and auditable
- Official order: group_scale → dq_init → emicorr → saturation → ipc → 
  firstframe → lastframe → reset → linearity → rscd → dark_current → 
  refpix → (common steps)

### 3. PROPER RAMP_FIT OUTPUT HANDLING
Current Implementation:
- Explicitly handles tuple return from `fit_signal_ramps()`: (rate_data, ints_model)
- Matches official JWST behavior where ramp_fit returns two products

Previous Approach:
- Ignored return values from ramp fitting

### 4. SEPARATE GAIN SCALE APPLICATIONS
Current Implementation:
- Applies gain_scale separately to rate product (_rate.fits) and ints_model 
  (_rateints.fits)
- Matches official pipeline behavior

Previous Approach:
- Called `apply_gain_scaling()` once, saved only _rateints.fits

### 5. ENABLED COMMON STEPS
Current Implementation:
- Calls both `charge_migration` and `clean_flicker_noise` steps
- Matches official pipeline behavior
- Persistence is correctly skipped (MIRI-specific)

### 6. SUPPORTED MODES
- **MiriImaging**: Direct imaging mode with calwebb_image2 processing
- **MiriLrs**: Low resolution spectroscopy with calwebb_spec2 processing

## Reference Implementation
Based on official JWST Pipeline:
https://github.com/spacetelescope/jwst/blob/main/jwst/pipeline/calwebb_detector1.py
