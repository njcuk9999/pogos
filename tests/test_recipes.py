from pogos.recipes import pogos_run
from pogos.recipes import pogos_setup
from pogos.core import definitions


def test_pogos_setup_main_orchestrates_setup_steps(monkeypatch):
    calls = []
    params = {
        "GLOBAL.LOCAL_DOWNLOAD_DATA": "/tmp/demo",
        "GLOBAL.DEMO_SYMLINK_DATA": True,
        "GLOBAL.YAML_FILE": "/tmp/pogos.yaml",
    }
    params.update({step.run_key: False for step in definitions.RED_STEPS})
    modules = pogos_setup.recipe_helpers.load_modules(
        ['tsovore', 'eureka_wrap', 'jwst_wrap', 'nameless_wrap',
         'sossisse_wrap', 'miriam', 'sorbet'])
    (tsovore, eureka_wrap, jwst_wrap, nameless_wrap,
     sossisse_wrap, miriam, sorbet) = modules
    monkeypatch.setattr(pogos_setup.recipe_helpers, 'load_modules',
                        lambda names: modules)

    monkeypatch.setattr(pogos_setup.general, "start_splash", lambda name: calls.append(("start", name)))
    monkeypatch.setattr(pogos_setup.general, "end_splash", lambda: calls.append(("end", None)))
    monkeypatch.setattr(pogos_setup.startup, "initial_setup", lambda: {"external": True})
    monkeypatch.setattr(
        pogos_setup.load_functions,
        "get_all_params",
        lambda **kwargs: calls.append(("get_all_params", kwargs["kwargs"])) or params,
    )
    monkeypatch.setattr(
        pogos_setup.startup,
        "setup",
        lambda in_params: calls.append(("setup", in_params is params)) or "CDICT",
    )
    monkeypatch.setattr(
        tsovore,
        "setup_tsovore_module",
        lambda in_params: calls.append(("tsovore", in_params is params)) or in_params,
    )
    monkeypatch.setattr(
        eureka_wrap,
        "setup_eureka_pre_extract",
        lambda in_params: calls.append(("pre_eureka", in_params is params)) or in_params,
    )
    monkeypatch.setattr(
        sossisse_wrap,
        "setup_sossisse_module",
        lambda in_params, cdict: calls.append(("sossisse", in_params is params, cdict == "CDICT")),
    )
    monkeypatch.setattr(
        miriam,
        "setup_miriam_module",
        lambda in_params: calls.append(("miriam", in_params is params)) or in_params,
    )
    monkeypatch.setattr(
        eureka_wrap,
        "setup_eureka_extract",
        lambda in_params: calls.append(("ext_eureka", in_params is params)) or in_params,
    )
    monkeypatch.setattr(
        sorbet,
        "setup_sorbet_module",
        lambda in_params: calls.append(("sorbet", in_params is params)) or in_params,
    )
    monkeypatch.setattr(
        eureka_wrap,
        "setup_eureka_post_extract",
        lambda in_params: calls.append(("post_eureka", in_params is params)) or in_params,
    )
    monkeypatch.setattr(
        pogos_setup.load_functions,
        "download_data",
        lambda in_params, demolocal, demosymlink: calls.append(
            ("download", in_params is params, demolocal, demosymlink)
        ),
    )
    monkeypatch.setattr(
        pogos_setup.startup,
        "check_crds",
        lambda in_params: calls.append(("check_crds", in_params is params)),
    )

    pogos_setup.main(
        yamlfile="/tmp/pogos.yaml",
        instrument_select=1,
        instrument_mode=1,
        preextract_step=1,
        extract_step=1,
        postextract_step="1",
    )

    assert ("start", "POGOS Setup") in calls
    assert ("get_all_params", {"yamlfile": "/tmp/pogos.yaml", "instrument_select": 1, "instrument_mode": 1, "preextract_step": 1, "extract_step": 1, "postextract_step": "1"}) in calls
    assert ("sossisse", True, True) in calls
    assert ("download", True, "/tmp/demo", True) in calls
    assert ("check_crds", True) in calls
    assert ("end", None) in calls


def test_pogos_run_main_routes_instances_between_steps(monkeypatch):
    tsovore_inst = {"name": "tsovore-inst"}
    params = {
        "GLOBAL.YAML_FILE": "/tmp/pogos.yaml",
        "RUN.TSOVORE": True,
        "RUN.PRE_EUREKA": False,
        "RUN.PRE_JWST": False,
        "RUN.PRE_NAMELESS": False,
        "RUN.EXT_BOX": False,
        "RUN.EXT_EUREKA": False,
        "RUN.EXT_JWST": False,
        "RUN.EXT_NAMELESS": False,
        "RUN.SOSSISSE": True,
        "RUN.MIRIAM": False,
        "RUN.POST_EUREKA": False,
        "RUN.POST_JWST": False,
        "RUN.SORBET.WLCA": False,
        "RUN.SORBET.SLCA": False,
    }
    modules = pogos_run.recipe_helpers.load_modules(
        ['tsovore', 'sossisse_wrap', 'miriam', 'sorbet',
         'jwst_wrap', 'nameless_wrap', 'eureka_wrap'])
    tsovore, sossisse_wrap, _, sorbet, _, _, _ = modules
    monkeypatch.setattr(pogos_run.recipe_helpers, 'load_modules',
                        lambda names: modules)

    calls = []
    monkeypatch.setattr(pogos_run.general, "start_splash", lambda name: calls.append(("start", name)))
    monkeypatch.setattr(pogos_run.general, "end_splash", lambda: calls.append(("end", None)))
    monkeypatch.setattr(pogos_run.startup, "quick_args", lambda argv: False)
    monkeypatch.setattr(pogos_run.startup, "initial_setup", lambda: {"external": True})
    monkeypatch.setattr(pogos_run.load_functions, "get_all_params", lambda **kwargs: params)
    monkeypatch.setattr(pogos_run.startup, "check_crds", lambda in_params: calls.append(("check_crds", in_params is params)))
    monkeypatch.setattr(pogos_run.startup, "check_red_steps", lambda in_params: calls.append(("check_red_steps", in_params is params)))
    monkeypatch.setattr(pogos_run.startup, "check_instrument_modes", lambda in_params: calls.append(("check_instrument_modes", in_params is params)))
    monkeypatch.setattr(
        tsovore,
        "run_tsovore",
        lambda in_params: calls.append(("run_tsovore", in_params is params)) or tsovore_inst,
    )
    monkeypatch.setattr(
        sossisse_wrap,
        "run_sossisse",
        lambda in_params, pre_inst: calls.append(
            ("run_sossisse", in_params is params, pre_inst.get("tsovore") is tsovore_inst)
        ) or {"name": "sossisse-inst"},
    )
    monkeypatch.setattr(sorbet, "any_sorbet_run", lambda in_params: False)

    pogos_run.main(yamlfile="/tmp/pogos.yaml")

    assert ("start", "POGOS") in calls
    assert ("run_tsovore", True) in calls
    assert ("run_sossisse", True, True) in calls
    assert ("check_crds", True) in calls
    assert ("check_red_steps", True) in calls
    assert ("check_instrument_modes", True) in calls
    assert ("end", None) in calls


def test_pogos_help_main_prints_beginner_friendly_command_guide(monkeypatch):
    from pogos.recipes import pogos_help

    calls = []

    monkeypatch.setattr(pogos_help.general, "start_splash",
                        lambda name: calls.append(("start", name)))
    monkeypatch.setattr(pogos_help.general, "end_splash",
                        lambda: calls.append(("end", None)))
    monkeypatch.setattr(pogos_help.startup, "quick_args", lambda argv: False)
    monkeypatch.setattr(
        pogos_help.help_text,
        "WLOG",
        lambda params, level, message, **kwargs: calls.append(
            ("log", level, message)
        ),
    )

    pogos_help.main()

    messages = [entry[2] for entry in calls if entry[0] == "log"]
    assert ("start", "POGOS Help") in calls
    assert ("end", None) in calls
    assert "POGOS command guide" in messages
    assert "Recommended first steps" in messages
    assert "pogos_setup" in messages
    assert "pogos_copy" in messages
    assert "pogos_config" in messages
    assert "pogos_run" in messages
    assert "Available reduction stages" in messages
