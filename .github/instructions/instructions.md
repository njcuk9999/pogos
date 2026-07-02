# POGOS Developer Instructions

This file captures project-specific rules and lessons learned while extending
POGOS flavors/modules.

## Flavor Integration Checklist

When adding a new flavor/wrapper module, update **all** of the following:

1. `pogos/core/base.py`
   - Add instrument support in `RED_STEPS` for Pre/Extraction/Post as needed.
   - Add run switches in `RUN_KEYS` (e.g. `RUN.PRE_X`, `RUN.EXT_X`, `RUN.POST_X`).
   - Add any shared-prefix disable entries in `SUB_RUN_KEYS`.
     - Use exact keys (e.g. `RUN.PRE_X`) for stage-specific prefixes.
     - Use wildcard keys (e.g. `RUN.*_X`) for shared groups disabled only when
       all matching run keys are False.
   - Add `RUN_DIRS` or `REQ_MODULE_PARAMS` entries when relevant.
   - If a wrapper uses a shared canonical root (not stage-specific roots), add
     its RUN keys to `SKIP_GENERIC_RUN_DIRS` so startup does not create empty
     generic folders like `pre_x`, `ext_x`, `post_x`.

2. `pogos/core/startup.py`
   - Ensure `initial_setup()` adds the module ConstDict under the correct
     namespace key used by params (example: `STD_JWST`, not `JWST`).
   - Keep heavy imports lazy (import inside helper functions) where possible.

3. `pogos/recipes/pogos_setup.py`
   - Wire the flavor into setup flow:
     - Pre-extract setup call(s)
     - Extraction setup call(s)
     - Post-extract setup call(s)
   - Keep `_LAZY_MODULES` and `_load_setup_modules()` updated.

4. `pogos/recipes/pogos_copy.py`
   - Mirror `pogos_setup.py` module setup wiring so copied YAMLs build all
     required module directories/params.
   - Keep `_LAZY_MODULES` and `_load_copy_modules()` updated.

5. `pogos/recipes/pogos_run.py`
   - Add run-stage execution hooks and instance routing in pre/extract/post
     sections.

6. Wrapper package `__init__.py`
   - Export canonical setup/run symbols expected by recipes.

## Namespace and Prefix Rules

- JWST standard pipeline config namespace is `STD_JWST.*`.
- Shared disable behavior is controlled by `SUB_RUN_KEYS` prefixes.
- Wildcard entries in `SUB_RUN_KEYS` are evaluated against RUN keys and applied
  only when all matching RUN keys are False.
- Generic run-directory creation in `startup.setup()` is skipped for RUN keys
  listed in `SKIP_GENERIC_RUN_DIRS` (currently Eureka, NAMELESS, STD_JWST).

## Startup Performance Rules

- Avoid heavy top-level imports in package `__init__.py` and recipe modules.
- Prefer lazy attribute/module loading using `__getattr__` for package exports.
- Keep Sorbet science stack (`juliet`, `exotic_ld`) runtime-only where possible.
- Keep external constants lazy-loaded in `startup.initial_setup()` (example:
  `SOSSISSE` ConstDict loaded there, not at `pogos.core.base` import time).

## Validation Before Merge

Run at least:

```bash
python -m py_compile pogos/recipes/pogos_setup.py pogos/recipes/pogos_copy.py pogos/recipes/pogos_run.py pogos/core/startup.py pogos/core/base.py
```

And, when touching startup/import behavior:

```bash
python -X importtime -c "import pogos.recipes.pogos_setup" 2> /tmp/pogos_setup_importtime.log
```

## Current Behavior Reference (2026-07)

- `pogos_setup` and `pogos_copy` both wire setup calls for:
  - `tsovore`
  - `eureka_wrap` (pre/extract/post)
  - `jwst_wrap` (pre/extract/post)
  - `nameless_wrap` (pre/extract)
  - `sossisse_wrap`
  - `miriam`
  - `sorbet`

