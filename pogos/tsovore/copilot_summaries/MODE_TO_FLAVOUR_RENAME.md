# MODE → FLAVOUR Rename Complete

## Summary

Successfully renamed all references from `MODE` to `FLAVOUR` throughout the codebase to better reflect the semantic meaning of the step configuration parameter.

## Changes Made

### 1. **Constants File** (`pogos/constants/tsovore.py`)

#### Renamed Constants:
- `DEFAULT_MODES` → `DEFAULT_FLAVOURS`
- All 37 step entries updated

#### Updated Loop Logic:
```python
# OLD:
value['MODE'] = DEFAULT_MODES.get(step, 'None')
if value['MODE'] in STEP_DESCS:
    if step in STEP_DESCS[value['MODE']]:

# NEW:
value['FLAVOUR'] = DEFAULT_FLAVOURS.get(step, 'None')
if value['FLAVOUR'] in STEP_DESCS:
    if step in STEP_DESCS[value['FLAVOUR']]:
```

### 2. **Instrument Base Class** (`pogos/tsovore/instruments/default.py`)

#### Updated Method: `from_step_args()`

**Old Signature:**
```python
def from_step_args(self, func_name: str) -> Tuple[bool, str,
                                                   Dict[str, Any], str]:
    # ...
    mode = self.tparams[f'{step_arg}'].get('MODE', 'None')
    # ...
    msg = ('\n\nRunning {0} mode={1}').format(step_name, mode)
    return run_step, mode, kwargs, suffix
```

**New Signature:**
```python
def from_step_args(self, func_name: str) -> Tuple[bool, str,
                                                   Dict[str, Any], str]:
    # ...
    flavour = self.tparams[f'{step_arg}'].get('FLAVOUR', 'None')
    # ...
    msg = ('\n\nRunning {0} flavour={1}').format(step_name, flavour)
    return run_step, flavour, kwargs, suffix
```

#### Updated All Call Sites:
- Changed: `run_step, mode, kwargs, suffix = self.from_step_args(func_name)`
- To: `run_step, flavour, kwargs, suffix = self.from_step_args(func_name)`
- Applied globally across all step methods in the file

## Verification

✅ **Constants Updated:**
- `DEFAULT_FLAVOURS`: 37 entries
- `DEFAULT_RUN`: 37 entries  
- `STEP_SUFFIX`: 37 entries

✅ **Sample Configuration:**
```
Step: GROUP_SCALE_STEP
  - RUN: True
  - FLAVOUR: jwst
  - SUFFIX: _groupscalestep.fits
```

✅ **Code Compilation:**
- `default.py`: Compiles without errors
- `tsovore.py`: Compiles without errors
- Constants module: Imports successfully

## Parameter Structure

Each step now has the following configuration:
```python
STEP.<STEP_NAME> = {
    'RUN': bool,          # Whether to run the step
    'FLAVOUR': str,       # Implementation flavour (e.g., 'jwst')
    'KWARGS': dict,       # Additional step-specific kwargs
    'SUFFIX': str         # Expected output file suffix
}
```

## Terminology

**FLAVOUR** now represents the implementation variant of a step:
- `'jwst'` - Official JWST pipeline implementation (default for all steps)
- Future variants could include custom implementations, test modes, etc.

This is more semantically accurate than "MODE" which could be confused with:
- Instrument modes (SOSS, imaging, spectroscopy, etc.)
- Processing modes (raw, calibrated, etc.)
- Operational modes (normal, test, debug, etc.)

## Files Modified

1. `/scratch3/jwst/pogos/pogos/constants/tsovore.py`
   - Renamed `DEFAULT_MODES` → `DEFAULT_FLAVOURS`
   - Updated step initialization loop

2. `/scratch3/jwst/pogos/pogos/tsovore/instruments/default.py`
   - Updated `from_step_args()` method signature and implementation
   - Updated docstrings to reference `flavour` instead of `mode`
   - Updated all ~100+ call sites throughout the file

## Status

✅ **COMPLETE** - All MODE→FLAVOUR references updated globally
✅ **TESTED** - Code compiles without errors
✅ **VERIFIED** - Constants module works with new naming
