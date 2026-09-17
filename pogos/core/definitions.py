#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Authoritative POGOS instrument-mode and reduction-step definitions."""
from typing import Dict, Tuple

from pogos.core.base_classes import InputFiles
from pogos.core.base_classes import InstMode
from pogos.core.base_classes import ReductionLevel
from pogos.core.base_classes import RedStep


def _headers(**kwargs: Tuple[str, ...]):
    """Build immutable, normalized FITS-header requirements."""
    return tuple((key, tuple(value.upper() for value in values))
                 for key, values in kwargs.items())


# =============================================================================
# Instrument modes
# =============================================================================
NIRISS_SOSS = InstMode(
    name='JWST.NIRISS.SOSS', instrument='JWST.NIRISS', label='SOSS',
    headers=_headers(INSTRUME=('NIRISS',), DETECTOR=('NIS',),
                     EXP_TYPE=('NIS_SOSS',), PUPIL=('GR700XD',)))
NIRISS_SOSS_SUPERSTRIPE = InstMode(
    name='JWST.NIRISS.SOSS.SUPERSTRIPE', instrument='JWST.NIRISS',
    label='SOSS.SUPERSTRIPE', enabled=False)
NIRISS_FGS = InstMode(
    name='JWST.NIRISS.FGS', instrument='JWST.NIRISS', label='FGS',
    headers=_headers(INSTRUME=('FGS',),
                     EXP_TYPE=('FGS_IMAGE', 'FGS_FOCUS')))
NIRISS_AMI = InstMode(
    name='JWST.NIRISS.AMI', instrument='JWST.NIRISS', label='AMI',
    enabled=False)

NIRSPEC_BOTS_PRISM = InstMode(
    name='JWST.NIRSPEC.BOTS.PRISM', instrument='JWST.NIRSPEC',
    label='BOTS.PRISM',
    headers=_headers(INSTRUME=('NIRSPEC',), DETECTOR=('NRS1', 'NRS2'),
                     EXP_TYPE=('NRS_BRIGHTOBJ',), GRATING=('PRISM',)))
NIRSPEC_BOTS_G395M = InstMode(
    name='JWST.NIRSPEC.BOTS.G395M', instrument='JWST.NIRSPEC',
    label='BOTS.G395M',
    headers=_headers(INSTRUME=('NIRSPEC',), DETECTOR=('NRS1', 'NRS2'),
                     EXP_TYPE=('NRS_BRIGHTOBJ',), GRATING=('G395M',)))
NIRSPEC_BOTS_G235M = InstMode(
    name='JWST.NIRSPEC.BOTS.G235M', instrument='JWST.NIRSPEC',
    label='BOTS.G235M',
    headers=_headers(INSTRUME=('NIRSPEC',), DETECTOR=('NRS1', 'NRS2'),
                     EXP_TYPE=('NRS_BRIGHTOBJ',), GRATING=('G235M',)))
NIRSPEC_BOTS_G140M = InstMode(
    name='JWST.NIRSPEC.BOTS.G140M', instrument='JWST.NIRSPEC',
    label='BOTS.G140M',
    headers=_headers(INSTRUME=('NIRSPEC',), DETECTOR=('NRS1', 'NRS2'),
                     EXP_TYPE=('NRS_BRIGHTOBJ',), GRATING=('G140M',)))
NIRSPEC_BOTS_G395H = InstMode(
    name='JWST.NIRSPEC.BOTS.G395H', instrument='JWST.NIRSPEC',
    label='BOTS.G395H',
    headers=_headers(INSTRUME=('NIRSPEC',), DETECTOR=('NRS1', 'NRS2'),
                     EXP_TYPE=('NRS_BRIGHTOBJ',), GRATING=('G395H',)))
NIRSPEC_BOTS_G235H = InstMode(
    name='JWST.NIRSPEC.BOTS.G235H', instrument='JWST.NIRSPEC',
    label='BOTS.G235H',
    headers=_headers(INSTRUME=('NIRSPEC',), DETECTOR=('NRS1', 'NRS2'),
                     EXP_TYPE=('NRS_BRIGHTOBJ',), GRATING=('G235H',)))
NIRSPEC_BOTS_G140H = InstMode(
    name='JWST.NIRSPEC.BOTS.G140H', instrument='JWST.NIRSPEC',
    label='BOTS.G140H',
    headers=_headers(INSTRUME=('NIRSPEC',), DETECTOR=('NRS1', 'NRS2'),
                     EXP_TYPE=('NRS_BRIGHTOBJ',), GRATING=('G140H',)))
NIRSPEC_FS = InstMode(
    name='JWST.NIRSPEC.FS', instrument='JWST.NIRSPEC', label='FS',
    enabled=False)
NIRSPEC_MOSS = InstMode(
    name='JWST.NIRSPEC.MOSS', instrument='JWST.NIRSPEC', label='MOSS',
    enabled=False)
NIRSPEC_IFU = InstMode(
    name='JWST.NIRSPEC.IFU', instrument='JWST.NIRSPEC', label='IFU',
    enabled=False)

NIRCAM_IMAGING = InstMode(
    name='JWST.NIRCAM.IMAGING', instrument='JWST.NIRCAM', label='IMAGING',
    headers=_headers(INSTRUME=('NIRCAM',),
                     EXP_TYPE=('NRC_IMAGE', 'NRC_TSIMAGE')))
NIRCAM_WFSS = InstMode(
    name='JWST.NIRCAM.WFSS', instrument='JWST.NIRCAM', label='WFSS',
    headers=_headers(INSTRUME=('NIRCAM',),
                     EXP_TYPE=('NRC_WFSS', 'NRC_TSGRISM')))
NIRCAM_MULTISTRIPE = InstMode(
    name='JWST.NIRCAM.MULTISTRIPE', instrument='JWST.NIRCAM',
    label='MULTISTRIPE', enabled=False)
NIRCAM_CORON = InstMode(
    name='JWST.NIRCAM.CORON', instrument='JWST.NIRCAM', label='CORON',
    enabled=False)
NIRCAM_TSO_IMAGING = InstMode(
    name='JWST.NIRCAM.TSO-IMAGING', instrument='JWST.NIRCAM',
    label='TSO-IMAGING', enabled=False)
NIRCAM_TSO_GRISM = InstMode(
    name='JWST.NIRCAM.TSO-GRISM', instrument='JWST.NIRCAM',
    label='TSO-GRISM', enabled=False)

MIRI_IMAGING = InstMode(
    name='JWST.MIRI.IMAGING', instrument='JWST.MIRI', label='IMAGING',
    headers=_headers(INSTRUME=('MIRI',), EXP_TYPE=('MIR_IMAGE',)))
MIRI_LRS = InstMode(
    name='JWST.MIRI.LRS', instrument='JWST.MIRI', label='LRS',
    headers=_headers(INSTRUME=('MIRI',),
                     EXP_TYPE=('MIR_LRS-FIXEDSLIT', 'MIR_LRS-SLITLESS')))
MIRI_MRS = InstMode(
    name='JWST.MIRI.MRS', instrument='JWST.MIRI', label='MRS', enabled=False)
MIRI_CORON = InstMode(
    name='JWST.MIRI.CORON', instrument='JWST.MIRI', label='CORON',
    enabled=False)
MIRI_WFSS = InstMode(
    name='JWST.MIRI.WFSS', instrument='JWST.MIRI', label='WFSS', enabled=False)

INST_MODES = (
    NIRISS_SOSS, NIRISS_SOSS_SUPERSTRIPE, NIRISS_FGS, NIRISS_AMI,
    NIRSPEC_BOTS_PRISM, NIRSPEC_BOTS_G395M, NIRSPEC_BOTS_G235M,
    NIRSPEC_BOTS_G140M, NIRSPEC_BOTS_G395H, NIRSPEC_BOTS_G235H,
    NIRSPEC_BOTS_G140H, NIRSPEC_FS, NIRSPEC_MOSS, NIRSPEC_IFU,
    NIRCAM_IMAGING, NIRCAM_WFSS, NIRCAM_MULTISTRIPE, NIRCAM_CORON,
    NIRCAM_TSO_IMAGING, NIRCAM_TSO_GRISM,
    MIRI_IMAGING, MIRI_LRS, MIRI_MRS, MIRI_CORON, MIRI_WFSS,
)
ENABLED_INST_MODES = tuple(mode for mode in INST_MODES if mode.enabled)
MODE_BY_NAME = {mode.name: mode for mode in INST_MODES}


# =============================================================================
# Reduction levels and steps
# =============================================================================
PRE_EXTRACTION = ReductionLevel('Pre-extraction', allow_multiple=False)
EXTRACTION = ReductionLevel('Extraction', allow_multiple=False)
POST_EXTRACTION = ReductionLevel('Post-extraction', allow_multiple=True)
REDUCTION_LEVELS = (PRE_EXTRACTION, EXTRACTION, POST_EXTRACTION)

NIRSPEC_BOTS_MODES = (
    NIRSPEC_BOTS_PRISM, NIRSPEC_BOTS_G395M, NIRSPEC_BOTS_G235M,
    NIRSPEC_BOTS_G140M, NIRSPEC_BOTS_G395H, NIRSPEC_BOTS_G235H,
    NIRSPEC_BOTS_G140H,
)
STANDARD_JWST_MODES = tuple(mode for mode in ENABLED_INST_MODES
                            if mode.standard_jwst)

TSOVORE = RedStep(
    'TSOVORE', 'RUN.TSOVORE', PRE_EXTRACTION,
    (NIRISS_SOSS,) + NIRSPEC_BOTS_MODES +
    (NIRCAM_IMAGING, NIRCAM_WFSS, MIRI_IMAGING),
    input_files=InputFiles('TSOVORE.INPUTS.FILES',
                           'TSOVORE.PATHS.INPUT_PATH'),
    mode_key='TSOVORE.INPUTS.INSTRUMENTMODE')
PRE_NAMELESS = RedStep(
    'PRE_NAMELESS', 'RUN.PRE_NAMELESS', PRE_EXTRACTION, (NIRISS_SOSS,),
    sub_prefixes=('NAMELESS.S1_SETTINGS', 'NAMELESS.S2_SETTINGS',
                  'NAMELESS.PREP_SETTINGS', 'NAMELESS.CST_SETTINGS'),
    shared_prefixes=('NAMELESS.GENERAL',), generic_run_dir=False)
PRE_EUREKA = RedStep(
    'PRE_EUREKA', 'RUN.PRE_EUREKA', PRE_EXTRACTION, STANDARD_JWST_MODES,
    sub_prefixes=('EUREKA.STAGE1', 'EUREKA.STAGE2'),
    shared_prefixes=('EUREKA.GENERAL',), generic_run_dir=False)
PRE_JWST = RedStep(
    'PRE_JWST', 'RUN.PRE_JWST', PRE_EXTRACTION, STANDARD_JWST_MODES,
    sub_prefixes=('STD_JWST.STAGE1', 'STD_JWST.STAGE2'),
    shared_prefixes=('STD_JWST.GENERAL',), generic_run_dir=False)

SOSSISSE = RedStep(
    'SOSSISSE', 'RUN.SOSSISSE', EXTRACTION,
    (NIRISS_SOSS,) + NIRSPEC_BOTS_MODES,
    input_files=InputFiles('SOSSISSE.GENERAL.FILES',
                           'SOSSISSE.PATHS.RAWPATH'),
    run_dir_key='SOSSISSE.INPUTS.SOSSIOPATH',
    required_params=('SOSSISSE.INPUTS.OBJECTNAME',),
    mode_key='SOSSISSE.INPUTS.INSTRUMENTMODE')
MIRIAM = RedStep(
    'MIRIAM', 'RUN.MIRIAM', EXTRACTION, (MIRI_IMAGING,),
    input_files=InputFiles('MIRIAM.INPUTS.FILES',
                           'MIRIAM.PATHS.INPUT_PATH'))
EXT_NAMELESS = RedStep(
    'EXT_NAMELESS', 'RUN.EXT_NAMELESS', EXTRACTION, (NIRISS_SOSS,),
    sub_prefixes=('NAMELESS.EXT_SETTINGS',),
    shared_prefixes=('NAMELESS.GENERAL',), generic_run_dir=False)
EXT_EUREKA = RedStep(
    'EXT_EUREKA', 'RUN.EXT_EUREKA', EXTRACTION, STANDARD_JWST_MODES,
    sub_prefixes=('EUREKA.STAGE3',), shared_prefixes=('EUREKA.GENERAL',),
    generic_run_dir=False)
EXT_JWST = RedStep(
    'EXT_JWST', 'RUN.EXT_JWST', EXTRACTION, STANDARD_JWST_MODES,
    sub_prefixes=('STD_JWST.STAGE3',),
    shared_prefixes=('STD_JWST.GENERAL',), generic_run_dir=False)
EXT_BOX = RedStep('EXT_BOX', 'RUN.EXT_BOX', EXTRACTION, ())

SORBET_WLCA = RedStep(
    'SORBET.WLCA', 'RUN.SORBET.WLCA', POST_EXTRACTION,
    (NIRISS_SOSS,) + NIRSPEC_BOTS_MODES + (MIRI_IMAGING,),
    shared_prefixes=('SORBET.GENERAL', 'SORBET.PLOTS'))
SORBET_SLCA = RedStep(
    'SORBET.SLCA', 'RUN.SORBET.SLCA', POST_EXTRACTION,
    (NIRISS_SOSS,) + NIRSPEC_BOTS_MODES,
    shared_prefixes=('SORBET.GENERAL', 'SORBET.PLOTS'))
POST_EUREKA = RedStep(
    'POST_EUREKA', 'RUN.POST_EUREKA', POST_EXTRACTION,
    STANDARD_JWST_MODES,
    sub_prefixes=('EUREKA.STAGE4', 'EUREKA.STAGE5', 'EUREKA.STAGE6'),
    shared_prefixes=('EUREKA.GENERAL',), generic_run_dir=False)
POST_JWST = RedStep(
    'POST_JWST', 'RUN.POST_JWST', POST_EXTRACTION, STANDARD_JWST_MODES,
    shared_prefixes=('STD_JWST.GENERAL',), generic_run_dir=False)

RED_STEPS = (
    TSOVORE, PRE_NAMELESS, PRE_EUREKA, PRE_JWST,
    SOSSISSE, MIRIAM, EXT_NAMELESS, EXT_EUREKA, EXT_JWST, EXT_BOX,
    SORBET_WLCA, SORBET_SLCA, POST_EUREKA, POST_JWST,
)
STEP_BY_NAME = {step.name: step for step in RED_STEPS}
STEP_BY_RUN_KEY = {step.run_key: step for step in RED_STEPS}


def steps_for_level(level: ReductionLevel) -> Tuple[RedStep, ...]:
    """Return reduction steps in declaration order for one level."""
    return tuple(step for step in RED_STEPS if step.level == level)


def mode_choices() -> Dict[str, Tuple[InstMode, ...]]:
    """Return visible instrument-mode choices grouped by instrument."""
    choices = {}
    for mode in INST_MODES:
        choices.setdefault(mode.instrument, [])
        choices[mode.instrument].append(mode)
    return {instrument: tuple(modes)
            for instrument, modes in choices.items()}


def validate_definitions():
    """Validate definition uniqueness and cross-references at import time."""
    if len(MODE_BY_NAME) != len(INST_MODES):
        raise ValueError('Instrument mode names must be unique')
    if len(STEP_BY_NAME) != len(RED_STEPS):
        raise ValueError('Reduction step names must be unique')
    if len(STEP_BY_RUN_KEY) != len(RED_STEPS):
        raise ValueError('Reduction step run keys must be unique')
    known_modes = set(INST_MODES)
    known_levels = set(REDUCTION_LEVELS)
    for step in RED_STEPS:
        if step.level not in known_levels:
            raise ValueError(f'Unknown reduction level for {step.name}')
        if not set(step.supported_modes).issubset(known_modes):
            raise ValueError(f'Unknown instrument mode in {step.name}')
    for mode in ENABLED_INST_MODES:
        if len(mode.headers) == 0:
            raise ValueError(f'No header rules defined for {mode.name}')


validate_definitions()
