import pickle

from pogos.core import definitions
from pogos.core.base_classes import InstMode


def test_definition_names_and_keys_are_unique():
    assert len(definitions.MODE_BY_NAME) == len(definitions.INST_MODES)
    assert len(definitions.STEP_BY_NAME) == len(definitions.RED_STEPS)
    assert len(definitions.STEP_BY_RUN_KEY) == len(definitions.RED_STEPS)


def test_reduction_levels_preserve_workflow_order_and_multiplicity():
    names = [level.name for level in definitions.REDUCTION_LEVELS]
    multiple = [level.allow_multiple for level in definitions.REDUCTION_LEVELS]
    assert names == ['Pre-extraction', 'Extraction', 'Post-extraction']
    assert multiple == [False, False, True]


def test_steps_reference_instrument_mode_objects():
    for step in definitions.RED_STEPS:
        assert all(isinstance(mode, InstMode) for mode in step.supported_modes)


def test_g235_modes_are_linked_to_sossisse():
    assert definitions.SOSSISSE.supports(definitions.NIRSPEC_BOTS_G235M)
    assert definitions.SOSSISSE.supports(definitions.NIRSPEC_BOTS_G235H)
    assert all('G253' not in mode.name for mode in definitions.INST_MODES)


def test_enabled_modes_have_header_validation_rules():
    assert all(len(mode.headers) > 0 for mode in definitions.ENABLED_INST_MODES)


def test_definitions_are_pickle_safe():
    objects = (definitions.INST_MODES + definitions.REDUCTION_LEVELS +
               definitions.RED_STEPS)
    assert pickle.loads(pickle.dumps(objects)) == objects
