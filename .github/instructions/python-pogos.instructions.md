---
description: "Use when writing or reviewing POGOS Python source and tests."
applyTo: '**/*.py'
---

# POGOS Python Rules

## Layout and Imports

- Start new Python modules with `#!/usr/bin/env python` and the UTF-8 encoding
  declaration. Use four spaces for indentation.
- Apply the companion grammar instructions, including the 79-character limit.
- Group standard-library, third-party, and local imports with blank lines.
- Avoid wildcard imports. Prefer importing a module when using multiple
  functions from it, and call those functions through the module namespace.
- Use separate imports unless parentheses are needed to satisfy line length.
- Keep expensive backend imports lazy where existing runtime boundaries do so.
- Put module constants after imports and before classes and functions.
- Separate top-level definitions with two blank lines. Follow existing section
  banners for variables, classes, functions, and worker functions as needed.
- Do not add empty sections or a demonstration main block to library modules.

## Comments and Docstrings

- Document modules, classes, and functions with descriptive docstrings.
- Follow local `:param`, `:return`, and `:raises` conventions. Explain units,
  shapes, optional values, mutations, filesystem effects, and errors when
  relevant. State whether a setting is user-facing or runtime-only.
- Comment most executable lines in scientific and validation workflows,
  normally immediately above the statement. Explain intent and assumptions,
  not merely the statement's spelling; continuations can share one comment.
- Keep SORBET descriptions instrument-neutral. Where behavior is specific,
  list its applicability and explain what happens for other instruments.
- A trace is a SOSS diffraction order or a NIRSpec detector (1=NRS1, 2=NRS2).
  Other instruments may use an unnumbered trace. Do not equate numbered traces
  with independently measured white-light curves unless the producer does so.

## Parameters and Validation

- Gather stable settings into meaningful locals near function entry. Keep
  conditional reads behind their guards and refresh after parameter mutation.
- Preserve `params.get('PREFIX')` views and use their relative `rget` reads.
  Require a value only when its consuming behavior cannot handle `None`.
- Keep wrappers responsible for framework parameters and unpack fixed-key
  parameter bags before calling independent numerical helpers.
- Preserve independent trace timestamps, calibrations, outputs, and fit state.
- Preserve existing user edits. Keep style changes limited to touched code.
- Validate behavior with focused tests. Run POGOS tests from `/tmp` when recipe
  imports reject the checkout directory. Run SOSSISSE tests in a separate
  process because POGOS dependency stubs can interfere with collection.