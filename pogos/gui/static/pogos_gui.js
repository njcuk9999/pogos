/* ==========================================================================
   POGOS gui - page logic (namespace P)

   Built on the shared aperocore gui scripts (GUI namespace). Sections:
     P          path bar (page lock), yaml lists, parameter tool tips
     P.setup    Setup tab (pogos_setup form)
     P.edit     Edit tab (yaml form / raw editor, review + save,
                pogos_edit)
     P.run      Run tab (pogos_run single process / batch script)
     P.tpl      batch templates
     P.act      Actions tab (pogos_config, pogos_reset, diffs)
     P.plots    Plots tab (tree + gallery)
     P.files    Files tab (project organiser)
   ========================================================================== */
GUI.config.storagePrefix = 'pogos-gui';
var P = {path: null, yamls: [], params: {}, extraYamls: []};

/* ---- helpers ------------------------------------------------------------ */
P.$ = function (id) { return document.getElementById(id); };

P.debounce = function (fn, ms) {
    // call fn once, ms after the last call
    var timer = null;
    return function () {
        var args = arguments;
        clearTimeout(timer);
        timer = setTimeout(function () { fn.apply(null, args); }, ms);
    };
};

P.pills = function (summary) {
    // html summary of a yaml (path, mode, project, steps, version)
    if (!summary) { return ''; }
    var html = '<span class="path">' + GUI.esc(summary.path) + '</span>';
    if (summary.error) {
        return html + ' <span class="pill bad">' + GUI.esc(summary.error) +
            '</span>';
    }
    if (summary.instmode) { html += ' <span class="pill run">' +
        GUI.esc(summary.instmode) + '</span>'; }
    if (summary.project) { html += ' <span class="pill">project: ' +
        GUI.esc(summary.project) + '</span>'; }
    (summary.steps || []).forEach(function (step) {
        html += ' <span class="pill ok">' + GUI.esc(step) + '</span>';
    });
    if (summary.version) { html += ' <span class="pill">v' +
        GUI.esc(summary.version) + '</span>'; }
    if (!summary.pogos) { html += ' <span class="pill warn">not a POGOS ' +
        'yaml?</span>'; }
    if (summary.mtime) { html += ' <span class="muted">modified ' +
        GUI.fmtAge(summary.mtime) + '</span>'; }
    return html;
};

/* ---- POGOS path (the page is locked until it is set) -------------------- */
P.setLocked = function (locked) {
    P.$('main-wrap').classList.toggle('locked', locked);
    P.$('pogos-path').classList.toggle('unset', locked);
    document.querySelectorAll('#tabbar button').forEach(function (btn) {
        if (btn.id !== 'tab-btn-info') { btn.disabled = locked; }
    });
    if (locked && GUI.currentTab !== 'info') { GUI.setTab('info'); }
};

P.pathOpened = function (path, info) {
    // the server accepted a POGOS path
    var first = P.path !== path;
    P.path = path;
    P.$('pogos-path').value = path;
    GUI.store('path', path);
    var status = P.$('path-status');
    status.className = 'path-status ok';
    status.textContent = info ? info.nyamls + ' yaml(s), ' + info.nprojects +
        ' project(s)' : '';
    P.setLocked(false);
    if (first) { P.refreshAll(); }
};

P.applyPath = function () {
    var path = P.$('pogos-path').value.trim();
    var status = P.$('path-status');
    if (!path) { GUI.toast('Enter the POGOS path', 'bad'); return; }
    GUI.post('api/pogos/path', {path: path}).then(function (res) {
        if (res.success) { P.pathOpened(res.info.path, res.info); return; }
        if (res.missing) {
            return GUI.confirm('Create POGOS path', '<code>' +
                GUI.esc(res.info.path) + '</code> does not exist. Create it ' +
                '(with <code>yamls/</code> and <code>projects/</code>)?',
                'Create').then(function (ok) {
                    if (!ok) { return; }
                    return GUI.post('api/pogos/path', {path: path,
                                                       create: true})
                        .then(function (res2) {
                            if (res2.success) {
                                P.pathOpened(res2.info.path, res2.info);
                            } else { GUI.toast(res2.message, 'bad'); }
                        });
                });
        }
        status.className = 'path-status bad';
        status.textContent = res.message;
    }).catch(GUI.fail);
};

P.autoOpenPath = function (path) {
    // open a remembered path without asking (only if it is valid - nothing
    //   is created; otherwise the page stays locked with the reason shown)
    if (!path) { return; }
    GUI.post('api/pogos/path', {path: path}).then(function (res) {
        if (res.success) { P.pathOpened(res.info.path, res.info); return; }
        var status = P.$('path-status');
        status.className = 'path-status bad';
        status.textContent = res.message || 'not a valid POGOS path';
    }).catch(function () { return null; });
};

P.browsePath = function () {
    GUI.pickFile({title: 'Choose the POGOS path', any: true, dirs: true,
                  start: P.$('pogos-path').value || ''})
        .then(function (path) {
            if (path) { P.$('pogos-path').value = path; P.applyPath(); }
        });
};

P.refreshAll = function () {
    // reload everything that depends on the POGOS path
    if (!P.path) { return; }
    P.loadYamls();
    P.tpl.refreshNames();
    if (GUI.currentTab === 'plots') { P.plots.refresh(); }
    if (GUI.currentTab === 'files') { P.files.refresh(); }
};

/* ---- yaml lists (Edit / Run / Actions selects) -------------------------- */
P.loadYamls = function () {
    return GUI.get('api/pogos/yamls').then(function (data) {
        P.yamls = data.yamls;
        ['edit-select', 'run-select', 'act-select'].forEach(P.fillYamlSelect);
        P.run.selected();
        P.act.selected();
    }).catch(GUI.fail);
};

P.summaryOf = function (path) {
    var all = P.yamls.concat(P.extraYamls);
    for (var it = 0; it < all.length; it++) {
        if (all[it].path === path) { return all[it]; }
    }
    return null;
};

P.fillYamlSelect = function (id) {
    var select = P.$(id);
    var current = select.value || GUI.recall('yaml-' + id, '');
    var html = '<option value="">-- choose a yaml (' + P.yamls.length +
        ' in yamls/) --</option>';
    P.yamls.forEach(function (y) {
        html += '<option value="' + GUI.esc(y.path) + '">' + GUI.esc(y.name) +
            (y.instmode ? '  [' + GUI.esc(y.instmode) + ']' : '') +
            (y.project ? '  ' + GUI.esc(y.project) : '') + '</option>';
    });
    if (P.extraYamls.length) {
        html += '<optgroup label="Other files">';
        P.extraYamls.forEach(function (y) {
            html += '<option value="' + GUI.esc(y.path) + '">' +
                GUI.esc(y.path) + '</option>';
        });
        html += '</optgroup>';
    }
    select.innerHTML = html;
    if (current && P.summaryOf(current)) { select.value = current; }
};

P.browseYaml = function (selectId) {
    // pick a yaml anywhere on disk and add it to the selects
    return GUI.pickFile({title: 'Open a yaml file', any: true,
                         ext: ['.yaml', '.yml'],
                         start: P.path ? P.path + '/yamls' : ''})
        .then(function (path) {
            if (!path) { return null; }
            return GUI.get('api/pogos/yaml', {path: path}).then(function (d) {
                if (!P.summaryOf(d.path)) { P.extraYamls.push(d.summary); }
                ['edit-select', 'run-select', 'act-select']
                    .forEach(P.fillYamlSelect);
                P.$(selectId).value = d.path;
                return d.path;
            });
        }).catch(GUI.fail);
};

P.selectYaml = function (selectId, path) {
    // choose a yaml in a select (adding it if needed)
    if (!P.summaryOf(path)) {
        P.extraYamls.push({path: path, name: GUI.basename(path)});
        ['edit-select', 'run-select', 'act-select'].forEach(P.fillYamlSelect);
    }
    P.$(selectId).value = path;
    GUI.store('yaml-' + selectId, path);
};

/* ---- parameter descriptions (hover tool tips) --------------------------- */
P.loadParams = function () {
    // descriptions of every POGOS constant (probed once by the server)
    return GUI.get('api/pogos/param_info').then(function (data) {
        P.params = data.params || {};
        P.docs.flavours = data.flavours || [];
        if (P.edit.outline) { P.edit.renderForm(); }
        if (GUI.currentTab === 'docs') { P.docs.renderList(); }
    }).catch(function (err) { console.log('param info: ' + err.message); });
};

P.paramMeta = function (info) {
    // "type: str | default: None | options: a, b" line of a constant
    if (!info) { return ''; }
    var parts = [];
    if (info.dtype) { parts.push('type: ' + info.dtype); }
    parts.push('default: ' + (info.default === null ? 'None' :
        (typeof info.default === 'object' ? JSON.stringify(info.default) :
         String(info.default))));
    if (info.options && info.options.length) {
        parts.push('options: ' + info.options.join(', '));
    }
    return parts.join('  |  ');
};

P.tipEl = null;
// tool tips show at most this many characters of a description
P.TIP_MAX = 420;

P.showTip = function (el, ev) {
    var key = el.getAttribute('data-param');
    var info = P.params[key];
    var extra = el.getAttribute('data-tip') || '';
    if (!info && !extra) { return; }
    if (!P.tipEl) {
        P.tipEl = document.createElement('div');
        P.tipEl.className = 'param-tip';
        document.body.appendChild(P.tipEl);
    }
    // long descriptions are cut: the full text is on the Docs tab
    var text = info ? (info.short || info.description) : '';
    var cut = text.length > P.TIP_MAX || (info && info.short &&
                                         info.short !== info.description);
    if (text.length > P.TIP_MAX) {
        text = text.slice(0, P.TIP_MAX).replace(/\s+\S*$/, '') + ' ...';
    } else if (cut) { text += ' ...'; }
    P.tipEl.innerHTML = '<span class="pt-key">' + GUI.esc(key) + '</span>' +
        GUI.esc(text) + (cut ? '<span class="pt-meta">Click the parameter ' +
        'name for the full description (Docs tab)</span>' : '') +
        (extra ? (info ? '\n\n' : '') + GUI.esc(extra) : '') +
        (info ? '<span class="pt-meta">' + GUI.esc(P.paramMeta(info)) +
         '</span>' : '');
    P.tipEl.style.display = 'block';
    P.moveTip(ev);
};

P.moveTip = function (ev) {
    if (!P.tipEl || P.tipEl.style.display !== 'block') { return; }
    var x = ev.clientX + 14;
    var y = ev.clientY + 16;
    var w = P.tipEl.offsetWidth;
    var h = P.tipEl.offsetHeight;
    if (x + w > window.innerWidth - 8) { x = window.innerWidth - w - 8; }
    if (y + h > window.innerHeight - 8) { y = ev.clientY - h - 12; }
    P.tipEl.style.left = Math.max(4, x) + 'px';
    P.tipEl.style.top = Math.max(4, y) + 'px';
};

P.hideTip = function () {
    if (P.tipEl) { P.tipEl.style.display = 'none'; }
};

document.addEventListener('mouseover', function (ev) {
    var el = ev.target.closest ? ev.target.closest('[data-param]') : null;
    if (el) { P.showTip(el, ev); } else { P.hideTip(); }
});
document.addEventListener('mousemove', P.moveTip);
document.addEventListener('click', function (ev) {
    // parameter names (and "more in Docs" links) show the full
    //   description over the page (the Docs tab is one click further)
    var el = ev.target.closest ? ev.target.closest('[data-doc]') : null;
    if (el && P.docs) {
        ev.preventDefault();
        P.hideTip();
        P.docs.popup(el.getAttribute('data-doc'));
    }
});
document.addEventListener('scroll', P.hideTip, true);

/* ==========================================================================
   Setup
   ========================================================================== */
P.setup = {choices: null, demos: [], demoKey: '', autoProject: null,
           demoCounts: null};

P.setup.init = function () {
    GUI.get('api/pogos/setup_choices').then(function (data) {
        P.setup.choices = data;
        // restore the last instrument / mode (if any)
        var wanted = GUI.recall('setup-mode', null);
        var inst = null;
        data.instruments.forEach(function (i) {
            i.modes.forEach(function (m) { if (m.name === wanted) {
                inst = i.number; } });
        });
        P.setup.renderInstruments(inst);
        P.setup.renderModes(inst ? wanted : null);
        // the demo counts of the mode cards (a slower probe)
        GUI.get('api/pogos/demo_counts').then(function (res) {
            P.setup.demoCounts = res.counts || {};
            P.setup.fillModeCounts();
        }).catch(function () {
            P.setup.demoCounts = false;
            P.setup.fillModeCounts();
        });
    }).catch(GUI.fail);
    ['setup-data-path', 'setup-yaml', 'setup-local']
        .forEach(function (id) {
            P.$(id).addEventListener('input', P.setup.changed);
        });
    P.$('setup-project').addEventListener('input', function () {
        // a typed name is never replaced by a demo project name
        P.setup.autoProject = null;
        P.setup.changed();
    });
    P.$('setup-symlink').onchange = P.setup.changed;
    P.$('setup-project').addEventListener('input',
                                          P.debounce(P.setup.checkName, 400));
    P.$('setup-demo-filter').oninput = P.setup.renderDemos;
    document.querySelectorAll('input[name="setup-dl"]').forEach(function (r) {
        r.onchange = function () {
            P.$('setup-local-row').style.display =
                P.setup.download() === 'local' ? '' : 'none';
            P.setup.markChoices('setup-download');
            P.setup.changed();
        };
    });
    P.setup.markChoices('setup-download');
};

P.setup.useGlobalPath = function () {
    P.$('setup-data-path').value = P.path || '';
    P.setup.changed();
};

P.setup.enable = function (section, on) {
    // grey out a section until the one before it is chosen
    P.$('setup-sec-' + section).classList.toggle('disabled', !on);
};

P.setup.instrument = function () {
    var checked = document.querySelector(
        'input[name="setup-instrument"]:checked');
    if (!checked || !P.setup.choices) { return null; }
    var number = Number(checked.value);
    return P.setup.choices.instruments.filter(function (inst) {
        return inst.number === number; })[0] || null;
};

P.setup.mode = function () {
    var checked = document.querySelector('input[name="setup-mode"]:checked');
    var inst = P.setup.instrument();
    if (!checked || !inst) { return null; }
    return inst.modes.filter(function (m) {
        return m.name === checked.value; })[0] || null;
};

P.setup.markChoices = function (containerId) {
    // highlight the selected choice cards of a container
    P.$(containerId).querySelectorAll('.choice').forEach(function (card) {
        var input = card.querySelector('input');
        card.classList.toggle('selected', !!(input && input.checked));
    });
};

P.setup.renderInstruments = function (selected) {
    // one card per instrument (with its number of supported modes)
    var holder = P.$('setup-instruments');
    holder.innerHTML = P.setup.choices.instruments.map(function (inst) {
        var nok = inst.modes.filter(function (m) { return m.enabled; })
            .length;
        return '<label class="choice' + (nok ? '' : ' disabled') + '">' +
            '<input type="radio" name="setup-instrument" value="' +
            inst.number + '"' + (inst.number === selected ? ' checked' : '') +
            (nok ? '' : ' disabled') + '><span><span class="choice-title">' +
            inst.number + '. ' + GUI.esc(inst.name) + '</span><span ' +
            'class="choice-desc">' + nok + ' of ' + inst.modes.length +
            ' modes supported</span></span></label>';
    }).join('');
    holder.querySelectorAll('input').forEach(function (input) {
        input.onchange = function () {
            P.setup.markChoices('setup-instruments');
            P.setup.renderModes(null);
        };
    });
    P.setup.markChoices('setup-instruments');
};

P.setup.renderModes = function (wanted) {
    // the mode cards of the chosen instrument (greyed until one is chosen)
    var inst = P.setup.instrument();
    var holder = P.$('setup-modes');
    P.setup.enable(3, !!inst);
    P.$('setup-mode-note').textContent = inst ? '(' + inst.name + ')' :
        '(choose an instrument first)';
    if (!inst) {
        holder.innerHTML = '';
        P.setup.renderSteps();
        return;
    }
    holder.innerHTML = inst.modes.map(function (m) {
        return '<label class="choice' + (m.enabled ? '' : ' disabled') +
            '"><input type="radio" name="setup-mode" value="' +
            GUI.esc(m.name) + '"' + (m.enabled ? '' : ' disabled') +
            (m.name === wanted ? ' checked' : '') + '><span><span ' +
            'class="choice-title">' + m.number + '. ' + GUI.esc(m.label) +
            '</span><span class="choice-desc">' + GUI.esc(m.name) +
            (m.enabled ? '' : ' - not yet supported') + '</span>' +
            (m.enabled ? '<span class="choice-desc mode-counts" ' +
             'data-mode="' + GUI.esc(m.name) + '"></span>' : '') +
            '</span></label>';
    }).join('');
    P.setup.fillModeCounts();
    holder.querySelectorAll('input').forEach(function (input) {
        input.onchange = function () {
            GUI.store('setup-mode', input.value);
            P.setup.markChoices('setup-modes');
            P.setup.renderSteps();
        };
    });
    P.setup.markChoices('setup-modes');
    P.setup.renderSteps();
};

P.setup.fillModeCounts = function () {
    // "Supported flavours (n) demos (m)" on every enabled mode card
    var inst = P.setup.instrument();
    if (!inst) { return; }
    P.$('setup-modes').querySelectorAll('.mode-counts').forEach(function (el) {
        var name = el.getAttribute('data-mode');
        var mode = inst.modes.filter(function (m) {
            return m.name === name; })[0];
        var nflav = mode ? mode.levels.reduce(function (n, level) {
            return n + level.steps.length; }, 0) : 0;
        var counts = P.setup.demoCounts;
        // null = still probing, false = the probe failed
        var ndemo = counts === null ? '...' : counts === false ? '?' :
            (counts[name] || 0);
        // green when there are some, red when none (grey while probing)
        var cls = function (n) {
            return typeof n !== 'number' ? 'muted' : n > 0 ? 'cnt-ok' :
                'cnt-none'; };
        el.innerHTML = 'Supported <span class="' + cls(nflav) +
            '">flavours (' + nflav + ')</span>   <span class="' +
            cls(ndemo) + '">demos (' + ndemo + ')</span>';
        el.title = 'flavours: reduction steps that support this mode; ' +
            'demos: every demo object x combination of its flavours';
    });
};

P.setup.renderSteps = function () {
    var mode = P.setup.mode();
    var holder = P.$('setup-steps');
    P.setup.enable(4, !!mode);
    P.setup.enable(5, !!mode);
    if (!mode) {
        holder.innerHTML = '<p class="muted">Choose an instrument mode ' +
            'first.</p>';
        P.setup.demos = [];
        P.setup.renderDemos();
        P.setup.changed();
        return;
    }
    if (mode.levels.length === 0) {
        holder.innerHTML = '<div class="notice warn">No reduction steps ' +
            'support ' + GUI.esc(mode.name) + ' yet.</div>';
        P.setup.changed();
        return;
    }
    var saved = GUI.recall('setup-steps-' + mode.name, {});
    holder.innerHTML = mode.levels.map(function (level, lit) {
        // multiple choice levels use check boxes (Skip is exclusive)
        var type = level.multiple ? 'checkbox' : 'radio';
        var name = 'setup-level-' + lit;
        var chosen = saved[level.name] || [];
        var html = '<div class="step-level"><h4 data-param="GLOBAL.' +
            GUI.esc(level.arg.toUpperCase()) + '">' + GUI.esc(level.name) +
            (level.multiple ? ' <span class="muted small">(choose any, or ' +
             'skip)</span>' : '') + '</h4><div class="choice-grid" id="' +
            name + '-grid">';
        html += '<label class="choice"><input type="' + type + '" name="' +
            name + '" value="" data-skip="1"' + (chosen.length ? '' :
            ' checked') + '><span><span class="choice-title">Skip</span>' +
            '<span class="choice-desc">no ' +
            GUI.esc(level.name.toLowerCase()) + ' step</span></span></label>';
        level.steps.forEach(function (step) {
            html += '<label class="choice" data-param="RUN.' +
                GUI.esc(step.name) + '"><input type="' + type + '" name="' +
                name + '" value="' + GUI.esc(step.name) + '"' +
                (chosen.indexOf(step.name) >= 0 ? ' checked' : '') +
                '><span><span class="choice-title">' + GUI.esc(step.name) +
                '</span><span class="choice-desc">option ' + step.number +
                '</span></span></label>';
        });
        return html + '</div></div>';
    }).join('');
    mode.levels.forEach(function (level, lit) {
        var inputs = holder.querySelectorAll('input[name="setup-level-' +
                                             lit + '"]');
        inputs.forEach(function (input) {
            input.onchange = function () {
                if (level.multiple) {
                    // Skip excludes the steps (and the steps exclude Skip)
                    var skip = holder.querySelector('input[name="setup-level-' +
                                                    lit + '"][data-skip]');
                    if (input === skip && skip.checked) {
                        inputs.forEach(function (other) {
                            if (other !== skip) { other.checked = false; }
                        });
                    } else if (input !== skip && input.checked) {
                        skip.checked = false;
                    }
                    var any = Array.prototype.some.call(inputs, function (o) {
                        return o.checked; });
                    if (!any) { skip.checked = true; }
                }
                P.setup.markChoices('setup-level-' + lit + '-grid');
                GUI.store('setup-steps-' + mode.name, P.setup.steps());
                P.setup.loadDemos(false);
                P.setup.changed();
            };
        });
        P.setup.markChoices('setup-level-' + lit + '-grid');
    });
    P.setup.loadDemos(false);
    P.setup.changed();
};

P.setup.steps = function () {
    // level name -> chosen step names (empty = skipped)
    var mode = P.setup.mode();
    var out = {};
    if (!mode) { return out; }
    mode.levels.forEach(function (level, lit) {
        out[level.name] = [];
        document.querySelectorAll('input[name="setup-level-' + lit +
                                  '"]:checked').forEach(function (input) {
            if (input.value) { out[level.name].push(input.value); }
        });
    });
    return out;
};

P.setup.nsteps = function () {
    var steps = P.setup.steps();
    return Object.keys(steps).reduce(function (n, key) {
        return n + steps[key].length; }, 0);
};

P.setup.loadDemos = function (force) {
    var mode = P.setup.mode();
    var holder = P.$('setup-demos');
    var steps = P.setup.steps();
    if (!mode || P.setup.nsteps() === 0) {
        // forget any demo request still in flight
        P.setup.demoCacheKey = null;
        holder.style.opacity = 1;
        P.setup.demos = [];
        P.setup.setDemo('');
        P.$('setup-demo-note').textContent = '(choose reduction steps first)';
        return;
    }
    if (force) { P.setup.demoCacheKey = null; }
    var key = mode.name + JSON.stringify(steps);
    if (key === P.setup.demoCacheKey) { return; }
    P.setup.demoCacheKey = key;
    P.$('setup-demo-note').textContent = 'loading demos (preloading at ' +
        'start up - a few seconds)...';
    holder.style.opacity = 0.5;
    GUI.get('api/pogos/demos', {instmode: mode.name,
                                steps: JSON.stringify(steps)})
        .then(function (data) {
            if (key !== P.setup.demoCacheKey) { return; }
            holder.style.opacity = 1;
            P.setup.demos = data.demos;
            P.$('setup-demo-note').textContent = '(' + data.demos.length +
                ' available)';
            var keep = data.demos.some(function (d) {
                return d.key === P.setup.demoKey; });
            P.setup.setDemo(keep ? P.setup.demoKey :
                            (data.demos.length ? data.demos[0].key : ''));
        }).catch(function (err) {
            holder.style.opacity = 1;
            P.setup.demoCacheKey = null;
            P.$('setup-demo-note').textContent = '';
            GUI.fail(err);
        });
};

P.setup.setDemo = function (key) {
    // choose a demo: its project name fills section 1 unless the user
    //   typed their own name
    P.setup.demoKey = key;
    var demo = P.setup.demos.filter(function (d) { return d.key === key; })[0];
    var input = P.$('setup-project');
    var current = input.value.trim();
    var auto = current === '' || current === P.setup.autoProject;
    if (auto) {
        input.value = demo && demo.project ? demo.project : '';
        P.setup.autoProject = input.value || null;
        P.$('setup-project').classList.remove('bad');
        if (input.value) { P.setup.checkName(); }
    }
    P.setup.renderDemos();
    P.setup.changed();
};

P.setup.renderDemos = function () {
    // one card per demo: a header (number, object, mode, keywords, choose
    //   button), the description and labelled tiles below it
    var holder = P.$('setup-demos');
    var filter = P.$('setup-demo-filter').value.toLowerCase();
    var tile = function (label, html, wide) {
        return '<div class="demo-tile' + (wide ? ' wide' : '') + '"><div ' +
            'class="demo-label">' + label + '</div><div class="demo-value">' +
            html + '</div></div>';
    };
    var pick = function (sel) {
        return '<span class="demo-pick">' + (sel ? '&#10004; Selected' :
                                             'Use this demo') + '</span>';
    };
    var dataHtml = function (lines) {
        // "SOURCE (details): FILE, FILE" -> source + files
        if (!lines || !lines.length) { return '<span class="muted">-' +
                                              '</span>'; }
        return '<ul class="demo-data">' + lines.map(function (line) {
            var cut = String(line).lastIndexOf('): ');
            if (cut < 0) { cut = String(line).indexOf(': ');
                           cut = cut < 0 ? -1 : cut - 1; }
            if (cut < 0) { return '<li>' + GUI.esc(line) + '</li>'; }
            return '<li><span class="demo-src">' +
                GUI.esc(line.substring(0, cut + 1)) + '</span> ' +
                '<code>' + GUI.esc(line.substring(cut + 3)) + '</code></li>';
        }).join('') + '</ul>';
    };
    var none = !P.setup.demoKey;
    var html = '<label class="demo-row demo-none' + (none ? ' selected' :
        '') + '"><input type="radio" name="setup-demo" value=""' +
        (none ? ' checked' : '') + '><div class="demo-head"><span ' +
        'class="demo-num">&ndash;</span><div class="demo-head-text"><div ' +
        'class="demo-title">No demo</div><div class="demo-desc">Start ' +
        'from default values (not recommended without help from the ' +
        'developers) - remaining parameters are asked in the console.' +
        '</div></div>' + pick(none) + '</div></label>';
    var shown = 0;
    P.setup.demos.forEach(function (demo) {
        var text = (demo.title + ' ' + demo.object + ' ' +
                    (demo.keywords || []).join(' ') + ' ' + demo.key + ' ' +
                    demo.description).toLowerCase();
        if (filter && text.indexOf(filter) < 0) { return; }
        shown++;
        var sel = demo.key === P.setup.demoKey;
        html += '<label class="demo-row' + (sel ? ' selected' : '') + '">' +
            '<input type="radio" name="setup-demo" value="' +
            GUI.esc(demo.key) + '"' + (sel ? ' checked' : '') + '>' +
            '<div class="demo-head"><span class="demo-num">' + demo.number +
            '</span><div class="demo-head-text"><div class="demo-title">' +
            GUI.esc(demo.object || demo.key) + ' <span class="pill run">' +
            GUI.esc(demo.instmode || P.setup.mode().label) + '</span>' +
            (demo.keywords || []).map(function (kw) {
                return ' <span class="pill">' + GUI.esc(kw) + '</span>';
            }).join('') + '</div><div class="demo-desc">' +
            GUI.esc(demo.description || demo.title || '') + '</div></div>' +
            pick(sel) + '</div><div class="demo-tiles">' +
            tile('Project name', '<code>' + GUI.esc(demo.project || '?') +
                 '</code>') +
            tile('Yaml file', '<code>' + GUI.esc(demo.id) + '.yaml</code>') +
            tile('Demo', '<code>' + GUI.esc(demo.key) + '</code><div ' +
                 'class="muted small">' + GUI.esc(demo.author) + ' &middot; ' +
                 GUI.esc(demo.date) + '</div>') +
            tile('Input data', dataHtml(demo.data), true) +
            '</div></label>';
    });
    if (P.setup.demos.length && shown === 0) {
        html += '<p class="muted">No demos match the filter.</p>';
    }
    holder.innerHTML = html;
    holder.querySelectorAll('input').forEach(function (input) {
        input.onchange = function () { P.setup.setDemo(input.value); };
    });
};

P.setup.download = function () {
    var input = document.querySelector('input[name="setup-dl"]:checked');
    return input ? input.value : 'run';
};

P.setup.form = function () {
    var mode = P.setup.mode();
    return {data_path: P.$('setup-data-path').value.trim() || P.path,
            project_name: P.$('setup-project').value.trim(),
            yaml_name: P.$('setup-yaml').value.trim(),
            instmode: mode ? mode.name : '', steps: P.setup.steps(),
            demo: P.setup.demoKey, download: P.setup.download(),
            demolocal: P.$('setup-local').value.trim(),
            demosymlink: P.$('setup-symlink').checked};
};

P.setup.validate = function () {
    // ask the server to check the whole form (resolves the preview)
    return GUI.post('api/pogos/preview', {action: 'setup',
                                          form: P.setup.form()});
};

P.setup.changed = P.debounce(function () {
    // update the yaml name hint and the cli equivalent
    if (!P.path || !P.setup.choices) { return; }
    var demo = P.setup.demos.filter(function (d) {
        return d.key === P.setup.demoKey; })[0];
    var dataPath = P.$('setup-data-path').value.trim() || P.path;
    P.$('setup-yaml').placeholder = demo ? '(blank = ' + demo.id + '.yaml)' :
        'required without a demo';
    P.$('setup-yaml-help').innerHTML = 'Saved in <code>' +
        GUI.esc(dataPath + '/yamls/') + '</code>.';
    P.setup.validate().then(function (res) {
        GUI.setCli('cli-setup', res.display || '');
        P.$('setup-cli-note').textContent = res.errors.length ?
            '(incomplete - ' + res.errors.length + ' item(s) to fix)' : '';
    }).catch(function () { return null; });
}, 250);

P.setup.checkName = function () {
    var name = P.$('setup-project').value.trim();
    var help = P.$('setup-project-help');
    if (!name) { return; }
    GUI.post('api/pogos/project_name', {name: name}).then(function (res) {
        P.$('setup-project').classList.toggle('bad', !res.valid);
        if (!res.valid) {
            help.innerHTML = '<span style="color:var(--danger)">' +
                GUI.esc(res.error) + '</span>';
        } else if (res.exists) {
            help.innerHTML = '<span style="color:var(--warn)">This project ' +
                'already exists - its directories will be reused.</span>';
        } else {
            help.innerHTML = 'Outputs go to <code>{data path}/projects/' +
                GUI.esc(name) + '/&lt;module&gt;/</code>' +
                (P.setup.autoProject === name ? ' (from the demo)' : '') +
                '.';
        }
    }).catch(function () { return null; });
};

P.setup.browseLocal = function () {
    GUI.pickFile({title: 'Local mirror of the POGOS data server', any: true,
                  dirs: true}).then(function (path) {
        if (path) { P.$('setup-local').value = path; P.setup.changed(); }
    });
};

P.setup.run = function () {
    // validate everything; problems are listed in a popup, otherwise
    //   pogos_setup runs (and saves the yaml)
    var form = P.setup.form();
    P.$('btn-setup').disabled = true;
    P.setup.validate().then(function (res) {
        P.$('btn-setup').disabled = false;
        if (res.errors.length) {
            GUI.dialog({id: 'setup-invalid', narrow: true,
                        title: 'Setup is not complete',
                        body: '<p>Please fix the following before saving:' +
                              '</p><ul class="setup-errors">' +
                              res.errors.map(function (err) {
                                  return '<li>' + GUI.esc(err) + '</li>';
                              }).join('') + '</ul>',
                        buttons: [{label: 'OK', cls: 'primary'}]});
            return;
        }
        var demo = P.setup.demos.filter(function (d) {
            return d.key === form.demo; })[0];
        // the yaml pogos_setup will write (for the follow up links)
        var name = form.yaml_name ? (/\.yaml$/.test(form.yaml_name) ?
            form.yaml_name : form.yaml_name + '.yaml') :
            (demo ? demo.id + '.yaml' : '');
        P.setup.expected = name ? form.data_path.replace(/\/$/, '') +
            '/yamls/' + name : null;
        P.$('setup-after').style.display = 'none';
        GUI.startJob('api/pogos/setup', {form: form}, GUI.consoles.setup);
    }).catch(function (err) {
        P.$('btn-setup').disabled = false;
        GUI.fail(err);
    });
};

P.setup.done = function (job) {
    // pogos_setup finished: offer the next steps
    P.loadYamls();
    var box = P.$('setup-after');
    if (job.returncode !== 0 || !P.setup.expected) { return; }
    var path = P.setup.expected;
    box.style.display = '';
    box.innerHTML = 'Setup finished: <code>' + GUI.esc(path) + '</code> ' +
        '<button class="small" id="setup-open-edit">Review in Edit</button> ' +
        '<button class="small primary" id="setup-open-run">Go to Run' +
        '</button>';
    P.$('setup-open-edit').onclick = function () { P.edit.open(path); };
    P.$('setup-open-run').onclick = function () {
        P.selectYaml('run-select', path);
        P.run.selected();
        GUI.setTab('run');
    };
};

/* ==========================================================================
   Edit
   ========================================================================== */
P.edit = {path: null, original: '', text: '', mtime: null, outline: null,
          edits: {}, view: 'form', openSecs: {}, added: {}};

P.edit.init = function () {
    // opening the tab loads the remembered / selected yaml
    GUI.onTab('edit', function () {
        var path = P.$('edit-select').value;
        if (!P.edit.path && path) { P.edit.load(path); }
    });
    P.$('edit-filter').oninput = P.debounce(function () {
        P.edit.renderForm(); }, 200);
    // the sticky section bar follows the scroll position
    window.addEventListener('scroll', P.debounce(function () {
        if (GUI.currentTab === 'edit') { P.edit.updateNav(); }
    }, 30), {passive: true});
    var raw = P.$('edit-raw');
    raw.addEventListener('input', function () {
        P.edit.text = raw.value;
        P.edit.updateGutter();
        P.edit.updateDirty();
    });
    raw.addEventListener('scroll', function () {
        P.$('edit-gutter').scrollTop = raw.scrollTop;
    });
    raw.addEventListener('keydown', function (ev) {
        if (ev.key === 'Tab') {
            ev.preventDefault();
            var start = raw.selectionStart;
            raw.setRangeText('  ', start, raw.selectionEnd, 'end');
            raw.dispatchEvent(new Event('input'));
        }
    });
    document.addEventListener('keydown', function (ev) {
        if ((ev.ctrlKey || ev.metaKey) && ev.key === 's' &&
            GUI.currentTab === 'edit' && P.edit.path) {
            ev.preventDefault();
            P.edit.save(false);
        }
    });
    window.addEventListener('beforeunload', function (ev) {
        if (P.edit.dirty()) { ev.preventDefault(); ev.returnValue = ''; }
    });
};

P.edit.dirty = function () {
    return !!P.edit.path && (Object.keys(P.edit.edits).length > 0 ||
                             P.edit.text !== P.edit.original);
};

P.edit.confirmDiscard = function () {
    if (!P.edit.dirty()) { return Promise.resolve(true); }
    return GUI.confirm('Unsaved changes', 'Discard the unsaved changes to ' +
                       '<code>' + GUI.esc(P.edit.path) + '</code>?',
                       'Discard');
};

P.edit.loadSelected = function () {
    var path = P.$('edit-select').value;
    if (!path || path === P.edit.path) { return; }
    P.edit.confirmDiscard().then(function (ok) {
        if (ok) { P.edit.load(path); }
        else { P.$('edit-select').value = P.edit.path || ''; }
    });
};

P.edit.browse = function () {
    P.edit.confirmDiscard().then(function (ok) {
        if (!ok) { return; }
        P.browseYaml('edit-select').then(function (path) {
            if (path) { P.edit.load(path); }
        });
    });
};

P.edit.open = function (path) {
    // open a yaml in the editor from another tab
    P.selectYaml('edit-select', path);
    GUI.setTab('edit');
    P.edit.confirmDiscard().then(function (ok) { if (ok) {
        P.edit.load(path); } });
};

P.edit.reload = function () {
    if (!P.edit.path) { return; }
    P.edit.confirmDiscard().then(function (ok) {
        if (ok) { P.edit.load(P.edit.path); }
    });
};

P.edit.load = function (path) {
    return GUI.get('api/pogos/yaml', {path: path}).then(function (data) {
        P.edit.path = data.path;
        P.edit.original = data.text;
        P.edit.text = data.text;
        P.edit.mtime = data.mtime;
        P.edit.edits = {};
        P.edit.added = {};
        GUI.store('yaml-edit-select', data.path);
        P.$('edit-summary').innerHTML = P.pills(data.summary) +
            (data.truncated ? ' <span class="pill bad">file too large - ' +
             'truncated</span>' : '');
        P.$('edit-card').style.display = '';
        P.$('edit-raw').value = data.text;
        P.edit.updateGutter();
        GUI.post('api/pogos/preview', {action: 'edit',
                                       form: {yaml: data.path}})
            .then(function (res) { GUI.setCli('cli-edit', res.display ||
                                              res.error); });
        return P.edit.refreshOutline();
    }).catch(GUI.fail);
};

P.edit.refreshOutline = function () {
    // parse the current text into the parameter form
    return GUI.post('api/yaml/outline', {text: P.edit.text})
        .then(function (outline) {
            P.edit.outline = outline;
            var err = P.$('edit-error');
            err.style.display = outline.error ? '' : 'none';
            err.textContent = outline.error ? 'YAML error: ' + outline.error :
                '';
            P.edit.renderForm();
            P.edit.updateDirty();
        });
};

P.edit.currentText = function () {
    // the text with the pending form edits applied (promise)
    var edits = Object.keys(P.edit.edits).map(function (line) {
        return P.edit.edits[line];
    });
    if (P.edit.view === 'raw' || edits.length === 0) {
        return Promise.resolve(P.edit.text);
    }
    return GUI.post('api/yaml/apply', {text: P.edit.text, edits: edits})
        .then(function (res) {
            if (res.errors.length) {
                GUI.toast(res.errors.join('\n'), 'bad');
            }
            return res.text;
        });
};

P.edit.setView = function (view) {
    if (view === P.edit.view) { return; }
    var done;
    if (view === 'raw') {
        // apply the form edits to the text first
        done = P.edit.currentText().then(function (text) {
            P.edit.text = text;
            P.edit.edits = {};
            P.$('edit-raw').value = text;
            P.edit.updateGutter();
        });
    } else {
        P.edit.text = P.$('edit-raw').value;
        done = P.edit.refreshOutline();
    }
    done.then(function () {
        P.edit.view = view;
        P.$('edit-view-form').classList.toggle('active', view === 'form');
        P.$('edit-view-raw').classList.toggle('active', view === 'raw');
        P.$('edit-form').style.display = view === 'form' ? '' : 'none';
        P.$('edit-raw-wrap').style.display = view === 'raw' ? '' : 'none';
        P.$('edit-filter').style.display = view === 'form' ? '' : 'none';
        P.edit.updateDirty();
    });
};

P.edit.updateGutter = function () {
    var count = P.$('edit-raw').value.split('\n').length;
    var nums = [];
    for (var it = 1; it <= count; it++) { nums.push(it); }
    P.$('edit-gutter').textContent = nums.join('\n');
};

P.edit.updateDirty = function () {
    var pill = P.$('edit-dirty');
    var nedits = Object.keys(P.edit.edits).length;
    var dirty = P.edit.dirty();
    pill.className = 'pill' + (dirty ? ' warn' : ' ok');
    pill.textContent = dirty ? (nedits ? nedits + ' unsaved change(s)' :
                                'unsaved changes') : 'saved';
};

P.edit.nodeValue = function (node) {
    // the (possibly edited) value of a node for the form
    var edit = P.edit.edits[node.line];
    if (edit) { return edit.items ? edit.items.join('\n') : edit.value; }
    return node.kind === 'list' ? node.items.join('\n') : node.value;
};

P.edit.inputHtml = function (node, choices) {
    // the editor widget of one node (choices = allowed values or null)
    var value = P.edit.nodeValue(node);
    var attrs = ' data-line="' + node.line + '"';
    if (node.kind === 'list') {
        return '<textarea' + attrs + ' rows="' +
            Math.min(8, Math.max(2, node.items.length + 1)) + '" ' +
            'placeholder="one item per line">' + GUI.esc(value) +
            '</textarea>';
    }
    if (node.kind !== 'scalar') {
        return '<div class="yf-readonly">(' + GUI.esc(node.kind) + ' - edit ' +
            'in Raw YAML)</div>';
    }
    if (node.vtype === 'bool' || /^(true|false)$/i.test(value)) {
        var lower = String(value).toLowerCase();
        return '<select' + attrs + '><option' + (lower === 'true' ?
            ' selected' : '') + '>true</option><option' + (lower === 'false' ?
            ' selected' : '') + '>false</option></select>';
    }
    var info = P.params[node.path.join('.')];
    var opts = choices || (info && info.options && info.options.length ?
                           info.options : null);
    if (opts) {
        opts = opts.slice();
        var clean = String(value).replace(/^['"]|['"]$/g, '');
        if (opts.indexOf(clean) < 0) { opts.unshift(clean); }
        return '<select' + attrs + '>' + opts.map(function (opt) {
            return '<option' + (opt === clean ? ' selected' : '') + '>' +
                GUI.esc(opt) + '</option>';
        }).join('') + '</select>';
    }
    return '<input type="text"' + attrs + ' value="' + GUI.esc(value) +
        '" spellcheck="false" placeholder="(empty)">';
};

// the help text shown under a parameter is cut after this many characters
//   (the full text is on the Docs tab)
P.HELP_MAX = 240;
// the sources a file constant can use
P.FILE_SOURCES = ['local', 'pogos', 'mast'];

P.helpHtml = function (key, text) {
    // a (shortened) description with a link to the full one in Docs
    if (!text) { return ''; }
    var more = text.length > P.HELP_MAX;
    var shown = more ? text.slice(0, P.HELP_MAX).replace(/\s+\S*$/, '') +
        '...' : text;
    return '<div class="yf-help">' + GUI.esc(shown) + (more ?
        ' <a class="doc-link" data-doc="' + GUI.esc(key) + '">more in ' +
        'Docs</a>' : '') + '</div>';
};

P.edit.rowHtml = function (node, label, choices, noHelp, helpText) {
    // one parameter row: key (click for Docs), widget, help and type line
    //   (noHelp: the help is already shown, e.g. by its file card;
    //    helpText: help to show instead of the constant description)
    var key = node.path.join('.');
    var info = P.params[key];
    var help = helpText || (noHelp ? '' : (info ? (info.short ||
                                           info.description) : node.comment));
    var changed = P.edit.isChanged(node);
    return '<div class="yf-row' + (changed ? ' changed' : '') +
        '" data-row="' + node.line + '"><div class="yf-key" data-param="' +
        GUI.esc(key) + '" data-doc="' + GUI.esc(key) + '">' +
        GUI.esc(label || node.key) + (info && !info.file ?
        P.edit.removeHtml(key) : '') + '<span class="yf-path">' +
        GUI.esc(node.path.slice(0, -1).join('.')) + ' &middot; line ' +
        (node.line + 1) + '</span></div><div class="yf-value">' +
        P.edit.inputHtml(node, choices) + P.helpHtml(key, help) +
        (info ? '<div class="yf-meta">' + GUI.esc(P.paramMeta(info)) +
         '</div>' : '') + '</div></div>';
};

// what each file source means (labels of the source switch)
P.FILE_SOURCE_LABELS = {local: 'files already on disk',
                        pogos: 'POGOS data server',
                        mast: 'MAST archive'};
// file sub keys that must have a value for a source
P.FILE_REQUIRED_KEYS = {local: ['filelist'], pogos: ['filelist', 'url'],
                        mast: ['pid', 'obsnumber', 'product']};
// file sub keys that are optional (not flagged when absent)
P.FILE_OPTIONAL_KEYS = ['match', 'min_size_mb'];
// help for the sub keys of a file constant
P.FILE_KEY_HELP = {
    filelist: 'The file name(s). For source: mast leave empty to use every ' +
        'matching MAST file (filled in after downloading).',
    always_download: 'True: download again on every run. False: only ' +
        'download when a listed file is missing.',
    url: 'The POGOS data server directory holding the files.',
    pid: 'JWST program ID e.g. 1366.',
    obsnumber: 'Observation number within the program e.g. 1.',
    product: 'The kind of file e.g. uncal, rateints, x1dints (for source: ' +
        'mast also the MAST file suffix used to find the files).',
    match: 'Optional: list of strings every filename must contain e.g. ' +
        '[nrs1].',
    min_size_mb: 'Optional: skip files smaller than this many MB.'
};

P.edit.fileSpec = function (key) {
    // the spec of a file constant (a fallback if it was not probed)
    var info = P.params[key];
    return (info && info.filespec) || {
        sources: P.FILE_SOURCES,
        base_keys: ['filelist', 'source', 'always_download', 'product'],
        source_keys: {local: [], pogos: ['url'],
                      mast: ['pid', 'obsnumber', 'match', 'min_size_mb']},
        defaults: {always_download: 'False', match: '[]',
                   min_size_mb: '1.0'},
        multi: true, product: null, product_options: null, extras: {}};
};

P.edit.fileKeys = function (spec, source) {
    // the keys written for one source (in yaml order)
    var keys = ['filelist', 'source'];
    keys = keys.concat(spec.source_keys[source] || []);
    if (source !== 'local' || spec.product) { keys.push('product'); }
    if (source !== 'local') { keys.push('always_download'); }
    // mast filters after the main keys
    var tail = ['match', 'min_size_mb'];
    keys = keys.filter(function (k) { return tail.indexOf(k) < 0; })
        .concat(keys.filter(function (k) { return tail.indexOf(k) >= 0; }));
    return keys.concat(Object.keys(spec.extras || {}));
};

P.edit.fileChildren = function (node) {
    // the child key nodes of a file constant
    var size = node.path.length;
    var key = node.path.join('.');
    return P.edit.outline.nodes.filter(function (n) {
        return n.line > node.line && n.path.length > size &&
            n.path.slice(0, size).join('.') === key;
    });
};

P.edit.fileSource = function (children) {
    var source = 'local';
    children.forEach(function (child) {
        if (child.key === 'source') {
            source = String(P.edit.nodeValue(child)).replace(/['"]/g, '')
                .trim() || 'local';
        }
    });
    return source;
};

P.edit.fileHtml = function (node, children) {
    // a file constant (FileObjectConst) as one card: a source switch and
    //   the sub fields of that source
    var key = node.path.join('.');
    var info = P.params[key];
    var spec = P.edit.fileSpec(key);
    var source = P.edit.fileSource(children);
    var nfiles = 0;
    children.concat([node]).forEach(function (n) {
        if (n.kind === 'list') { nfiles = n.items.length; }
    });
    var changed = children.concat([node]).some(function (n) {
        return !!P.edit.edits[n.line]; });
    var wanted = P.edit.fileKeys(spec, source);
    var present = children.map(function (c) { return c.key; });
    var absent = children.length ? wanted.filter(function (k) {
        return present.indexOf(k) < 0; }) : [];
    // match / min_size_mb (mast) are optional - only offered
    var missing = absent.filter(function (k) {
        return P.FILE_OPTIONAL_KEYS.indexOf(k) < 0; });
    var optional = absent.filter(function (k) {
        return P.FILE_OPTIONAL_KEYS.indexOf(k) >= 0; });
    var switcher = '<span class="yf-src-switch" title="Where the files ' +
        'come from - switching rewrites the sub fields">' +
        spec.sources.map(function (src) {
            return '<button type="button" class="' + (src === source ?
                'active' : '') + '" data-file-line="' + node.line +
                '" data-file-src="' + GUI.esc(src) + '" title="' +
                GUI.esc(P.FILE_SOURCE_LABELS[src] || src) + '">' +
                GUI.esc(src) + '</button>';
        }).join('') + '</span>';
    var html = '<div class="yf-file' + (changed ? ' changed' : '') + '">' +
        '<div class="yf-file-head"><span class="yf-file-icon">&#128196;' +
        '</span><span class="yf-file-name" data-param="' + GUI.esc(key) +
        '" data-doc="' + GUI.esc(key) + '">' + GUI.esc(node.key) + '</span>' +
        P.edit.removeHtml(key) + '<span class="pill">file</span>' +
        (nfiles ? '<span class="pill">' +
        nfiles + ' file(s)</span>' : '') + '<span class="yf-src-label">' +
        'Source</span>' + switcher + '<span class="muted small">' +
        GUI.esc(P.FILE_SOURCE_LABELS[source] || '') + '</span><span ' +
        'class="yf-path">' + GUI.esc(node.path.slice(0, -1).join('.')) +
        ' &middot; line ' + (node.line + 1) + '</span></div>' +
        P.helpHtml(key, info ? (info.short || info.description) : '') +
        (missing.length ? '<div class="notice warn small yf-file-note">' +
         'Not set for source ' + GUI.esc(source) + ': <code>' +
         missing.map(GUI.esc).join('</code>, <code>') + '</code> <button ' +
         'type="button" class="small" data-file-line="' + node.line +
         '" data-file-src="' + GUI.esc(source) + '">Add them</button>' +
         '</div>' : '') + (optional.length && !missing.length ? '<div ' +
         'class="muted small yf-file-note">Optional keys for source ' +
         GUI.esc(source) + ': <code>' + optional.map(GUI.esc)
         .join('</code>, <code>') + '</code> <button type="button" ' +
         'class="small" data-file-line="' + node.line + '" data-file-src="' +
         GUI.esc(source) + '">Add</button></div>' : '') +
        '<div class="yf-file-body">';
    if (children.length === 0) {
        // short form: a file name / list of local files (or empty)
        html += P.edit.rowHtml(node, 'filelist', null, true,
                               P.FILE_KEY_HELP.filelist);
    } else {
        children.forEach(function (child) {
            if (child.key === 'source') { return; }
            var choices = null;
            var help = P.FILE_KEY_HELP[child.key];
            var extra = (spec.extras || {})[child.key];
            if (child.key === 'product' && spec.product_options) {
                choices = spec.product_options;
            } else if (extra) {
                choices = extra.options || null;
                help = extra.description || help;
            }
            if ((P.FILE_REQUIRED_KEYS[source] || []).indexOf(child.key) >= 0
                && /^(|~|null|''|"")$/i.test(String(P.edit.nodeValue(child))
                                             .trim())) {
                help = 'REQUIRED for source ' + source + ' - ' + (help || '');
            }
            if (wanted.indexOf(child.key) < 0) {
                help = '(not used by source ' + source + ' - removed when ' +
                    'you switch source) ' + (help || '');
            }
            html += P.edit.rowHtml(child, child.key, choices, false,
                                   help || ' ');
        });
    }
    return html + '</div></div>';
};

P.edit.switchSource = function (line, source) {
    // rewrite a file constant for a source: keep the values that still
    //   apply, add the keys the source needs (with defaults) and drop the
    //   others - pending form edits are applied at the same time
    var node = P.edit.outline.nodes.filter(function (n) {
        return n.line === line; })[0];
    if (!node) { return; }
    var key = node.path.join('.');
    var spec = P.edit.fileSpec(key);
    var children = P.edit.fileChildren(node);
    var current = {};
    var raw = function (n) {
        var edit = P.edit.edits[n.line];
        if (n.kind === 'list' || (edit && edit.items)) {
            return {items: edit && edit.items ? edit.items : n.items};
        }
        return {value: edit ? edit.value : n.value};
    };
    if (children.length === 0) {
        current.filelist = raw(node);
    } else {
        children.forEach(function (c) {
            if (c.path.length === node.path.length + 1) {
                current[c.key] = raw(c);
            }
        });
    }
    var defaults = spec.defaults || {};
    var mapping = P.edit.fileKeys(spec, source).map(function (sub) {
        if (sub === 'source') { return {key: sub, value: source}; }
        if (current[sub]) {
            return Object.assign({key: sub}, current[sub]);
        }
        var value = defaults[sub] || '';
        if (sub === 'product' && spec.product) { value = spec.product; }
        var extra = (spec.extras || {})[sub];
        if (extra && extra.default !== null && extra.default !== undefined) {
            value = String(extra.default);
        }
        return {key: sub, value: value};
    });
    // an empty local file is written in the short form ("KEY:") - POGOS
    //   refuses a long form local entry without a filelist
    var blank = function (entry) {
        return entry.items ? entry.items.length === 0 :
            /^(|~|null|''|""|\[\])$/i.test(String(entry.value).trim());
    };
    if (source === 'local' && blank(mapping[0]) &&
        mapping.every(function (entry) {
            return ['filelist', 'source'].indexOf(entry.key) >= 0 ||
                blank(entry) || (entry.key === 'product' &&
                                 entry.value === spec.product);
        })) {
        mapping = [];
    }
    // the other pending edits (not inside this constant)
    var inside = [node.line].concat(children.map(function (c) {
        return c.line; }));
    var edits = Object.keys(P.edit.edits).filter(function (l) {
        return inside.indexOf(Number(l)) < 0;
    }).map(function (l) { return P.edit.edits[l]; });
    edits.push({line: node.line, key: node.key, mapping: mapping});
    GUI.post('api/yaml/apply', {text: P.edit.text, edits: edits})
        .then(function (res) {
            if (res.errors.length) {
                GUI.toast(res.errors.join('\n'), 'bad');
                return;
            }
            P.edit.text = res.text;
            P.edit.edits = {};
            P.$('edit-raw').value = res.text;
            P.edit.updateGutter();
            return P.edit.refreshOutline().then(function () {
                GUI.toast(node.key + ': source ' + source, 'ok');
            });
        }).catch(GUI.fail);
};

P.edit.renderForm = function () {
    var outline = P.edit.outline;
    var holder = P.$('edit-form');
    if (!outline) { holder.innerHTML = ''; return; }
    var filter = P.$('edit-filter').value.toLowerCase();
    var changedOnly = P.$('edit-changed-only').checked;
    // group the nodes by their top level key
    var sections = [];
    var current = null;
    outline.nodes.forEach(function (node) {
        if (node.depth === 0) {
            current = {node: node, rows: []};
            sections.push(current);
            if (node.kind === 'map') { return; }
        }
        if (current) { current.rows.push(node); }
    });
    var matches = function (node, key, help) {
        return !filter || (key + ' ' + P.edit.nodeValue(node) + ' ' +
                           (help || '')).toLowerCase().indexOf(filter) >= 0;
    };
    var html = '';
    var flat = !!filter || changedOnly;
    sections.forEach(function (sec) {
        var rows = '';
        var shown = 0;
        var nparams = 0;
        // the open sub-section boxes (keys) - closed when a row is not
        //   inside them any more (not used while filtering: flat list)
        var groups = [];
        var ngroups = 0;
        var closeGroups = function (key) {
            while (groups.length && key.indexOf(
                groups[groups.length - 1] + '.') !== 0) {
                rows += '</div></details>';
                groups.pop();
            }
        };
        for (var it = 0; it < sec.rows.length; it++) {
            var node = sec.rows[it];
            var key = node.path.join('.');
            if (!flat) { closeGroups(key); }
            var info = P.params[key];
            var help = info ? (info.short || info.description) : node.comment;
            // a file constant takes its sub keys with it
            if (info && info.file) {
                var children = [];
                while (it + 1 < sec.rows.length &&
                       sec.rows[it + 1].path.length > node.path.length &&
                       sec.rows[it + 1].path.slice(0, node.path.length)
                           .join('.') === key) {
                    children.push(sec.rows[++it]);
                }
                nparams++;
                var group = children.concat([node]);
                var changedFile = group.some(P.edit.isChanged);
                if (changedOnly && !changedFile) { continue; }
                if (filter && !group.some(function (n) {
                    return matches(n, key, help); })) { continue; }
                shown++;
                rows += P.edit.fileHtml(node, children);
                continue;
            }
            if (node.kind === 'map') {
                if (flat) { continue; }
                // a sub-section: a coloured box that can be closed
                var gopen = P.edit.openSecs[key] !== undefined ?
                    P.edit.openSecs[key] : true;
                rows += '<details class="yf-group-box g' + (ngroups % 6) +
                    ' depth' + Math.min(groups.length, 3) + '" ' +
                    'data-sec="' + GUI.esc(key) + '" data-nav="' +
                    GUI.esc(key) + '"' + (gopen ? ' open' : '') + '>' +
                    '<summary class="yf-group" data-param="' + GUI.esc(key) +
                    '">' + GUI.esc(node.path.slice(1).join('.')) +
                    (node.section ? ' <span class="yf-group-desc">- ' +
                     GUI.esc(node.section) + '</span>' : '') + '</summary>' +
                    '<div class="yf-group-body">';
                groups.push(key);
                ngroups++;
                continue;
            }
            nparams++;
            if (changedOnly && !P.edit.isChanged(node)) { continue; }
            if (!matches(node, key, help)) { continue; }
            shown++;
            rows += P.edit.rowHtml(node);
        }
        // close the sub-sections left open at the end of the section
        closeGroups('');
        if ((filter || changedOnly) && shown === 0) { return; }
        var name = sec.node.key;
        var saved = P.edit.openSecs[name];
        var isOpen = saved !== undefined ? saved :
            (name === 'GLOBAL' || name === 'RUN' || !!filter || changedOnly);
        html += '<details class="yf-section" data-sec="' + GUI.esc(name) +
            '" data-nav="' + GUI.esc(name) + '"' + (isOpen ? ' open' : '') +
            '><summary data-param="' +
            GUI.esc(name) + '">' + GUI.esc(name) + ' <span ' +
            'class="yf-count">' + (sec.node.section ? GUI.esc(
                sec.node.section) + ' &middot; ' : '') + nparams +
            ' parameter(s)</span></summary>' + (sec.node.kind === 'map' ?
            rows : P.edit.rowHtml(sec.node)) + '</details>';
    });
    holder.innerHTML = html || '<p class="muted">No parameters match.</p>';
    holder.querySelectorAll('details').forEach(function (det) {
        det.addEventListener('toggle', function (ev) {
            // nested details: only record the box that was toggled
            if (ev.target !== det) { return; }
            P.edit.openSecs[det.getAttribute('data-sec')] = det.open;
            P.edit.updateNav();
        });
    });
    P.edit.updateNav();
    holder.querySelectorAll('[data-file-src]').forEach(function (btn) {
        btn.onclick = function (ev) {
            ev.preventDefault();
            var line = Number(btn.getAttribute('data-file-line'));
            var src = btn.getAttribute('data-file-src');
            // (the switch's active button does nothing - "Add" buttons
            //   rewrite with the same source)
            if (btn.classList.contains('active')) { return; }
            P.edit.switchSource(line, src);
        };
    });
    holder.querySelectorAll('[data-remove]').forEach(function (btn) {
        btn.onclick = function (ev) {
            // (not the Docs link of the key around it)
            ev.preventDefault();
            ev.stopPropagation();
            P.edit.removeParam(btn.getAttribute('data-remove'));
        };
    });
    holder.querySelectorAll('[data-line]').forEach(function (input) {
        var handler = function () { P.edit.fieldChanged(input); };
        input.addEventListener('input', handler);
        input.addEventListener('change', handler);
    });
};

P.edit.updateNav = function () {
    // the sticky "where am I" bar: the innermost open section / sub-section
    //   whose header has scrolled past the bar
    var bar = P.$('edit-nav');
    if (!bar) { return; }
    var form = P.$('edit-form');
    if (P.edit.view !== 'form' || !form.offsetParent) {
        bar.style.display = 'none';
        return;
    }
    // stick just below the (sticky) top bar, whatever its height
    var navbar = document.querySelector('.navbar');
    bar.style.top = (navbar ? navbar.offsetHeight : 0) + 'px';
    var limit = bar.getBoundingClientRect().bottom + 2;
    var current = null;
    form.querySelectorAll('details[open][data-nav]').forEach(function (det) {
        var box = det.getBoundingClientRect();
        // a box that starts above the bar and still reaches below it
        if (box.top < limit && box.bottom > limit) {
            var path = det.getAttribute('data-nav');
            if (!current || path.length > current.length) { current = path; }
        }
    });
    bar.style.display = '';
    if (!current) {
        bar.innerHTML = '<span class="muted">' + (P.edit.path ?
            GUI.esc(GUI.basename(P.edit.path)) : '') + '</span>';
        return;
    }
    var parts = current.split('.');
    bar.innerHTML = '<span class="muted">' + GUI.esc(GUI.basename(
        P.edit.path || '')) + '</span>' + parts.map(function (part, it) {
            return ' <span class="nav-sep">&rsaquo;</span> <a data-goto="' +
                GUI.esc(parts.slice(0, it + 1).join('.')) + '">' +
                GUI.esc(part) + '</a>';
        }).join('');
    bar.querySelectorAll('[data-goto]').forEach(function (link) {
        link.onclick = function () {
            var target = form.querySelector('details[data-nav="' +
                link.getAttribute('data-goto').replace(/"/g, '\\"') + '"]');
            if (!target) { return; }
            var top = target.getBoundingClientRect().top + window.scrollY -
                (limit - 2) - 4;
            window.scrollTo({top: top, behavior: 'smooth'});
        };
    });
};

P.edit.fieldChanged = function (input) {
    var line = Number(input.getAttribute('data-line'));
    var node = P.edit.outline.nodes.filter(function (n) {
        return n.line === line; })[0];
    if (!node) { return; }
    var original = node.kind === 'list' ? node.items.join('\n') : node.value;
    var value = input.value;
    if (input.tagName === 'SELECT' && node.kind === 'scalar' &&
        /^['"].*['"]$/.test(node.value) && value !== original) {
        // keep the quoting of quoted option values
        value = "'" + value.replace(/'/g, "''") + "'";
    }
    if (value === original || (input.tagName === 'SELECT' &&
        value === original.replace(/^['"]|['"]$/g, ''))) {
        delete P.edit.edits[line];
    } else if (node.kind === 'list') {
        P.edit.edits[line] = {line: line, key: node.key,
                              items: value.split('\n').filter(function (v) {
                                  return v.trim() !== ''; })};
    } else {
        P.edit.edits[line] = {line: line, key: node.key, value: value};
    }
    var row = input.closest('.yf-row');
    if (row) { row.classList.toggle('changed', !!P.edit.edits[line]); }
    P.edit.updateDirty();
};

P.edit.isChanged = function (node) {
    // edited in the form, or added since the file was loaded
    return !!P.edit.edits[node.line] || !!P.edit.added[node.path.join('.')];
};

// ---- add parameters (any POGOS / flavour constant) ----
P.edit.presentKeys = function () {
    // every key already in the open file (sections included)
    var keys = {};
    ((P.edit.outline || {}).nodes || []).forEach(function (node) {
        keys[node.path.join('.')] = true;
    });
    return keys;
};

P.edit.yamlDefault = function (info) {
    // the default as written in a yaml (file constants: their mapping)
    return info.yaml !== undefined ? info.yaml : info.default;
};

P.edit.addDialog = function () {
    if (!P.edit.path) { return; }
    if (Object.keys(P.params).length === 0) {
        GUI.toast('The parameter list is still loading', 'bad');
        return;
    }
    GUI.addParams({
        title: 'Add parameters to ' + GUI.basename(P.edit.path),
        intro: 'Every POGOS constant that is not in this yaml yet (by ' +
               'default only the sections already in the file - choose ' +
               '<b>All sections</b> for the other flavours). Click ' +
               '<b>+</b> to add one with its default value: it is added ' +
               'as an unsaved change, so edit its value in the form, then ' +
               'review and save. Click a name for its full description.',
        defaultLabel: 'Default',
        section: 'file',
        params: function () {
            var out = {};
            Object.keys(P.params).forEach(function (key) {
                var info = P.params[key];
                out[key] = {description: info.short || info.description,
                            dtype: info.file ? 'file' : info.dtype,
                            advanced: !info.user,
                            value: P.edit.yamlDefault(info)};
            });
            return out;
        },
        present: P.edit.presentKeys,
        add: P.edit.addParams
    });
};

P.edit.addParams = function (keys) {
    // add parameters to the open yaml (as an unsaved change)
    var entries = keys.map(function (key) {
        var info = P.params[key] || {};
        return {key: key, value: P.edit.yamlDefault(info),
                description: info.short || info.description || '',
                dtype: info.dtype || null};
    });
    if (P.edit.view === 'raw') { P.edit.text = P.$('edit-raw').value; }
    return P.edit.currentText().then(function (text) {
        return GUI.yamlAdd(text, entries);
    }).then(function (res) {
        if (res.errors && res.errors.length) {
            GUI.toast(res.errors.join('\n'), 'bad');
        }
        if (!res.added || !res.added.length) { return false; }
        P.edit.text = res.text;
        P.edit.edits = {};
        P.$('edit-raw').value = res.text;
        P.edit.updateGutter();
        // highlight the added rows (and open their sections)
        res.added.forEach(function (key) {
            P.edit.added[key] = true;
            P.edit.openSecs[key.split('.')[0]] = true;
        });
        GUI.toast('Added ' + res.added.join(', ') + ' (not saved yet)');
        return P.edit.refreshOutline().then(function () { return true; });
    }).catch(function (err) { GUI.fail(err); return false; });
};

// ---- remove a parameter (back to its default) ----
P.edit.removeHtml = function (key) {
    // the "remove" button of a known constant
    if (!P.edit.path || !P.params[key]) { return ''; }
    return '<button type="button" class="yf-remove" data-remove="' +
        GUI.esc(key) + '" title="Remove ' + GUI.esc(key) + ' from the ' +
        'yaml (use the default value)">&#10005;</button>';
};

P.edit.removeParam = function (key) {
    // take a constant out of the open yaml (as an unsaved change) so its
    //   default is used again
    var info = P.params[key] || {};
    var node = ((P.edit.outline || {}).nodes || []).filter(function (n) {
        return n.path.join('.') === key; })[0];
    var current = '';
    if (node && node.kind !== 'map') { current = P.edit.nodeValue(node); }
    GUI.confirmRemove({key: key, file: GUI.basename(P.edit.path),
                       known: !!P.params[key], current: current,
                       value: info.default, defaultLabel: 'POGOS default'})
        .then(function (ok) {
            if (!ok) { return; }
            if (P.edit.view === 'raw') { P.edit.text = P.$('edit-raw').value; }
            return P.edit.currentText().then(function (text) {
                return GUI.yamlRemove(text, [key]);
            }).then(function (res) {
                if (res.errors && res.errors.length) {
                    GUI.toast(res.errors.join('\n'), 'bad');
                }
                if (!res.removed || !res.removed.length) { return; }
                P.edit.text = res.text;
                P.edit.edits = {};
                P.$('edit-raw').value = res.text;
                res.removed.forEach(function (k) { delete P.edit.added[k]; });
                P.edit.updateGutter();
                GUI.toast('Removed ' + res.removed.join(', ') + ' (not ' +
                          'saved yet)');
                return P.edit.refreshOutline();
            });
        }).catch(GUI.fail);
};

P.edit.revert = function () {
    if (!P.edit.path) { return; }
    P.edit.confirmDiscard().then(function (ok) {
        if (!ok) { return; }
        P.edit.text = P.edit.original;
        P.edit.edits = {};
        P.edit.added = {};
        P.$('edit-raw').value = P.edit.text;
        P.edit.updateGutter();
        P.edit.refreshOutline();
    });
};

P.edit.review = function () {
    if (!P.edit.path) { return; }
    P.edit.currentText().then(function (text) {
        GUI.showDiff({left_text: P.edit.original, right_text: text,
                      left_name: P.edit.path + ' (on disk)',
                      right_name: P.edit.path + ' (edited)',
                      title: 'Review changes'});
    });
};

P.edit.save = function (saveAs) {
    if (!P.edit.path) { return; }
    P.edit.currentText().then(function (text) {
        var doSave = function (target, force) {
            return GUI.post('api/pogos/yaml_save', {
                path: target, text: text, force: force,
                mtime: target === P.edit.path ? P.edit.mtime : null
            }).then(function (res) {
                if (res.conflict) {
                    return GUI.confirm('File changed on disk', GUI.esc(
                        res.message), 'Save anyway').then(function (ok) {
                        if (ok) { return doSave(target, true); }
                    });
                }
                GUI.toast(res.message, res.success ? 'ok' : 'bad');
                if (!res.success) { return; }
                P.loadYamls();
                P.selectYaml('edit-select', res.path);
                return P.edit.load(res.path);
            }).catch(GUI.fail);
        };
        var showReview = function (target) {
            if (text === P.edit.original && target === P.edit.path) {
                GUI.toast('No changes to save');
                return;
            }
            GUI.showDiff({left_text: P.edit.original, right_text: text,
                          left_name: P.edit.path,
                          right_name: target + ' (to be saved)',
                          title: 'Save ' + GUI.basename(target) + '?',
                          buttons: [{label: 'Cancel'},
                                    {label: 'Save', cls: 'primary',
                                     onclick: function (close) {
                                         close();
                                         doSave(target, false);
                                     }}]});
        };
        if (!saveAs) { showReview(P.edit.path); return; }
        var def = P.edit.path.replace(/(\.ya?ml)$/, '_copy$1');
        GUI.dialog({id: 'save-as', title: 'Save as', narrow: true,
                    body: '<label class="field-label">New yaml file</label>' +
                          '<input type="text" id="save-as-path" ' +
                          'style="width:100%" value="' + GUI.esc(def) + '">' +
                          '<p class="muted small">Note: this only writes a ' +
                          'copy of the file. To create a new project with ' +
                          'its own directories use <b>New project from ' +
                          'this yaml</b>.</p>',
                    buttons: [{label: 'Cancel'},
                              {label: 'Review and save', cls: 'primary',
                               onclick: function (close) {
                                   var target = P.$('save-as-path').value
                                       .trim();
                                   close();
                                   if (target) { showReview(target); }
                               }}]});
    });
};

P.edit.copyProject = function () {
    if (!P.edit.path) { GUI.toast('Load a yaml first', 'bad'); return; }
    var start = function () {
        GUI.startJob('api/pogos/edit', {yaml: P.edit.path},
                     GUI.consoles.edit);
    };
    if (P.edit.dirty()) {
        GUI.confirm('Unsaved changes', 'pogos_edit copies the yaml on ' +
                    'disk - your unsaved changes are not included. ' +
                    'Continue?', 'Continue').then(function (ok) {
            if (ok) { start(); } });
        return;
    }
    start();
};

/* ==========================================================================
   Run
   ========================================================================== */
P.run = {info: null, infoFor: null, loading: null};

P.run.yaml = function () { return P.$('run-select').value; };

P.run.selected = function () {
    var path = P.run.yaml();
    if (path) { GUI.store('yaml-run-select', path); }
    P.$('run-summary').innerHTML = path ? P.pills(P.summaryOf(path)) : '';
    P.run.loadInfo();
    P.run.updateCli();
    P.run.previewBatch();
};

P.run.init = function () {
    // files may have been downloaded meanwhile: re-check on entering Run
    GUI.onTab('run', function () {
        if (P.run.yaml() && !P.run.loading) { P.run.loadInfo(); }
    });
    P.run.setReady(false, 'choose a yaml first');
};

P.run.setReady = function (ready, note) {
    // the run buttons wait for the yaml summary (and its file checks)
    document.querySelectorAll('#tab-run .run-go').forEach(function (btn) {
        btn.disabled = !ready;
    });
    document.querySelectorAll('#tab-run .run-go-note').forEach(function (el) {
        el.textContent = note || '';
    });
};

P.run.loadInfo = function () {
    // load the yaml summary + input file status (before a run is allowed)
    var path = P.run.yaml();
    var holder = P.$('run-info');
    P.run.info = null;
    P.run.infoFor = null;
    P.run.loading = path || null;
    if (!path) {
        holder.innerHTML = '';
        P.run.setReady(false, 'choose a yaml first');
        return;
    }
    P.run.setReady(false, 'checking the yaml input files...');
    if (!holder.innerHTML) {
        holder.innerHTML = '<div class="notice">Loading the yaml summary ' +
            'and checking its input files (a few seconds the first time)' +
            '...</div>';
    } else {
        holder.style.opacity = 0.5;
    }
    GUI.get('api/pogos/yaml_files', {yaml: path}).then(function (info) {
        if (P.run.loading !== path) { return; }
        P.run.loading = null;
        P.run.info = info;
        P.run.infoFor = path;
        holder.style.opacity = 1;
        P.run.renderInfo();
        P.run.setReady(true, '');
    }).catch(function (err) {
        if (P.run.loading !== path) { return; }
        P.run.loading = null;
        holder.style.opacity = 1;
        holder.innerHTML = '<div class="notice bad">Could not check the ' +
            'yaml: ' + GUI.esc(err.message || err) + ' <button ' +
            'class="small" id="run-info-retry">Retry</button></div>';
        P.$('run-info-retry').onclick = P.run.loadInfo;
        // still allow the run (pogos_run reports the problem itself)
        P.run.setReady(true, 'yaml check failed - see above');
    });
};

P.run.fileStates = {
    ok: ['ok', 'on disk'],
    cached: ['run', 'in download cache (linked at run start)'],
    download: ['warn', 'to download at run start'],
    pending: ['warn', 'not retrieved yet (downloads at run start)'],
    missing: ['bad', 'missing'],
    chained: ['', 'made by an earlier step'],
    unset: ['', 'not set'],
    error: ['bad', 'error']
};

P.run.renderInfo = function () {
    var info = P.run.info;
    var holder = P.$('run-info');
    if (!info) { holder.innerHTML = ''; return; }
    var sum = info.summary || {};
    var demo = info.demo;
    var tile = function (label, html, wide) {
        return '<div class="demo-tile' + (wide ? ' wide' : '') + '"><div ' +
            'class="demo-label">' + label + '</div><div class="demo-value">' +
            html + '</div></div>';
    };
    var code = function (text) {
        return text ? '<code>' + GUI.esc(text) + '</code>' :
            '<span class="muted">-</span>';
    };
    // ---- header (as the demo cards) ----
    var html = '<div class="demo-row run-card"><div class="demo-head">' +
        '<div class="demo-head-text"><div class="demo-title">' +
        GUI.esc(demo ? (demo.object || demo.key) : sum.name) +
        (sum.instmode ? ' <span class="pill run">' +
         GUI.esc(sum.instmode) + '</span>' : '') +
        (demo ? (demo.keywords || []).map(function (kw) {
            return ' <span class="pill">' + GUI.esc(kw) + '</span>';
        }).join('') : '') + '</div><div class="demo-desc">' +
        GUI.esc(demo ? (demo.description || demo.title || '') :
                'Not a known demo project - the summary comes from the ' +
                'yaml itself.') + '</div></div><button class="small" ' +
        'id="run-info-refresh" title="check the files on disk again">' +
        '&#8635; Re-check files</button></div><div class="demo-tiles">';
    html += tile('Project name', code(sum.project));
    html += tile('Yaml file', code(sum.name) + '<div class="muted small">' +
                 (sum.version ? 'POGOS v' + GUI.esc(sum.version) : '') +
                 (info.version_ok ? '' : ' <span class="pill warn">older ' +
                  'version - needs Accept old</span>') + '</div>');
    html += tile('Flavours', (sum.steps || []).length ?
                 (sum.steps || []).map(function (st) {
                     return '<span class="pill ok">' + GUI.esc(st) +
                         '</span>'; }).join(' ') :
                 '<span class="pill bad">no steps enabled</span>');
    html += tile('Data path', code(sum.data_path));
    if (demo) {
        html += tile('Demo', code(demo.key) + '<div class="muted small">' +
                     GUI.esc(demo.author || '') + ' &middot; ' +
                     GUI.esc(demo.date || '') + '</div>');
    }
    // ---- input file status ----
    var files = info.files || [];
    var counts = info.counts || {};
    var bad = counts.missing || 0;
    var errs = counts.error || 0;
    var fetch = (counts.download || 0) + (counts.pending || 0);
    var notice;
    if (bad || errs) {
        notice = '<div class="notice bad">' + (bad ? bad + ' input file ' +
            'parameter(s) point at local files that are not on disk' : '') +
            (bad && errs ? '; ' : '') + (errs ? errs + ' could not be ' +
            'checked' : '') + '.</div>';
    } else if (fetch) {
        notice = '<div class="notice warn">' + fetch + ' input file ' +
            'parameter(s) are not retrieved yet - <code>pogos_run</code> ' +
            'downloads them at the start of the run (a batch job needs ' +
            'internet access on its node).</div>';
    } else {
        notice = '<div class="notice ok">All input files of the enabled ' +
            'steps are ready.</div>';
    }
    var rows = files.map(function (f, it) {
        var st = P.run.fileStates[f.status] || ['', f.status];
        var nfile = f.files.length;
        var nok = nfile - f.nmissing;
        var detail = '';
        if (nfile) {
            detail = '<details><summary class="small">' + nok + ' / ' +
                nfile + ' on disk' + '</summary><ul class="run-files">' +
                f.files.map(function (item) {
                    return '<li class="' + (item.exists ? 'ok' : 'bad') +
                        '"><span class="run-file-mark">' + (item.exists ?
                        '&#10004;' : (item.cached ? '&#8635;' : '&#10008;')) +
                        '</span><code title="' + GUI.esc(item.path) + '">' +
                        GUI.esc(item.name) + '</code>' + (item.link ?
                        ' <span class="muted small">(link)</span>' : '') +
                        (!item.exists && item.cached ? ' <span class="muted' +
                         ' small">in download cache</span>' : '') + '</li>';
                }).join('') + '</ul></details>';
        } else if (f.status === 'pending') {
            detail = '<span class="muted small">file list comes from the ' +
                'source</span>';
        }
        return '<tr class="run-file-row ' + GUI.esc(f.status) + '"><td>' +
            '<span class="mono small" data-param="' + GUI.esc(f.key) + '">' +
            GUI.esc(f.key) + '</span></td><td class="small">' +
            GUI.esc(f.label || (f.set ? f.source : '')) + '</td><td>' +
            '<span class="pill ' + st[0] + '">' + GUI.esc(st[1]) +
            '</span>' + (f.error ? '<div class="small st-error">' +
            GUI.esc(f.error) + '</div>' : '') + '</td><td>' + detail +
            '</td><td class="mono small run-dir">' + GUI.esc(f.directory ||
            '') + '</td></tr>';
    }).join('');
    html += tile('Input files (' + files.length + ' parameter(s) of the ' +
                 'enabled steps)', notice + (files.length ? '<div ' +
                 'class="table-wrap"><table class="run-files-table"><thead>' +
                 '<tr><th>Parameter</th><th>Source</th><th>Status</th>' +
                 '<th>Files</th><th>Directory</th></tr></thead><tbody>' +
                 rows + '</tbody></table></div>' : ''), true);
    html += '</div></div>';
    holder.innerHTML = html;
    P.$('run-info-refresh').onclick = P.run.loadInfo;
};

P.run.checkFiles = function () {
    // resolve true to go ahead (asks first if local files are missing)
    var info = P.run.info;
    if (!info || P.run.infoFor !== P.run.yaml() || !info.counts ||
        !info.counts.missing) {
        return Promise.resolve(true);
    }
    return GUI.confirm('Input files missing', info.counts.missing +
                       ' input file parameter(s) point at local files ' +
                       'that are not on disk - the run will probably ' +
                       'fail. Run anyway?', 'Run anyway');
};

P.run.browse = function () {
    P.browseYaml('run-select').then(function () { P.run.selected(); });
};

P.run.openInEdit = function () {
    if (P.run.yaml()) { P.edit.open(P.run.yaml()); }
};

P.run.form = function () {
    return {yaml: P.run.yaml(), accept_old: P.$('run-accept-old').checked,
            stream_plots: P.$('run-stream-plots').checked};
};

P.run.updateCli = function () {
    if (!P.path) { return; }
    GUI.post('api/pogos/preview', {action: 'run', form: P.run.form()})
        .then(function (res) { GUI.setCli('cli-run', res.display ||
                                          res.error); })
        .catch(function () { return null; });
    P.run.previewBatch();
};

P.run.runLocal = function () {
    if (!P.run.yaml()) { GUI.toast('Choose a yaml first', 'bad'); return; }
    if (P.run.loading) { GUI.toast('Still checking the yaml', 'bad'); return; }
    P.run.checkFiles().then(function (ok) {
        if (ok) { GUI.startJob('api/pogos/run', P.run.form(),
                               GUI.consoles.run); }
    });
};

P.run.batchForm = function (extra) {
    var form = P.run.form();
    form.template = P.$('batch-template').value;
    form.submit = P.$('batch-submit').checked;
    Object.keys(extra || {}).forEach(function (k) { form[k] = extra[k]; });
    return form;
};

P.run.previewBatch = P.debounce(function () {
    if (!P.path || !P.run.yaml()) {
        P.$('batch-preview').textContent = '(choose a yaml)';
        return;
    }
    GUI.post('api/pogos/batch', P.run.batchForm({preview: true}))
        .then(function (res) { P.$('batch-preview').textContent = res.text; })
        .catch(function (err) {
            P.$('batch-preview').textContent = err.message; });
}, 300);

P.run.batch = function () {
    if (!P.run.yaml()) { GUI.toast('Choose a yaml first', 'bad'); return; }
    if (P.run.loading) { GUI.toast('Still checking the yaml', 'bad'); return; }
    P.run.checkFiles().then(function (ok) { if (ok) { P.run.doBatch(); } });
};

P.run.doBatch = function () {
    GUI.post('api/pogos/batch', P.run.batchForm()).then(function (res) {
        var box = P.$('batch-result');
        box.style.display = '';
        box.className = 'notice ' + (res.success ? 'ok' : 'bad');
        box.innerHTML = GUI.esc(res.message) + (res.script ?
            '<br><code>' + GUI.esc(res.script) + '</code> <button ' +
            'class="small" id="batch-view">View script</button>' : '') +
            (res.job_id ? ' <button class="small" id="batch-procs">' +
             'Processes</button>' : '');
        if (P.$('batch-view')) {
            P.$('batch-view').onclick = function () {
                GUI.viewText(res.script); };
        }
        if (P.$('batch-procs')) {
            P.$('batch-procs').onclick = function () {
                GUI.setTab('processes'); };
        }
    }).catch(GUI.fail);
};

/* ---- batch templates ---------------------------------------------------- */
P.tpl = {fields: []};

P.tpl.refreshNames = function () {
    return GUI.get('api/templates').then(function (data) {
        P.tpl.fields = data.fields;
        P.$('batch-no-sbatch').style.display = data.sbatch ? 'none' : '';
        if (!data.sbatch) { P.$('batch-submit').checked = false; }
        ['batch-template', 'tpl-load'].forEach(function (id) {
            var select = P.$(id);
            var current = select.value;
            select.innerHTML = data.names.map(function (name) {
                return '<option>' + GUI.esc(name) + '</option>';
            }).join('');
            if (current && data.names.indexOf(current) >= 0) {
                select.value = current;
            }
        });
        P.tpl.load(P.$('tpl-load').value);
        P.run.previewBatch();
    }).catch(GUI.fail);
};

P.tpl.load = function (name) {
    return GUI.get('api/template', {name: name}).then(function (tpl) {
        P.$('tpl-name').value = name || 'default';
        P.$('tpl-fields').innerHTML = P.tpl.fields.map(function (field) {
            return '<div class="field"><label class="field-label">' +
                GUI.esc(field.replace(/_/g, ' ')) + '</label><input ' +
                'type="text" data-tpl="' + field + '" value="' +
                GUI.esc(tpl[field] === undefined ? '' : tpl[field]) +
                '"></div>';
        }).join('');
        P.$('tpl-activation').value = (tpl.activation || []).join('\n');
    }).catch(GUI.fail);
};

P.tpl.save = function () {
    var form = {name: P.$('tpl-name').value.trim() || 'default',
                activation: P.$('tpl-activation').value};
    document.querySelectorAll('[data-tpl]').forEach(function (input) {
        form[input.getAttribute('data-tpl')] = input.value;
    });
    GUI.post('api/template', form).then(function (res) {
        P.$('tpl-saved').textContent = res.message;
        GUI.toast(res.message, 'ok');
        P.tpl.refreshNames().then(function () {
            P.$('batch-template').value = form.name;
            P.$('tpl-load').value = form.name;
            P.run.previewBatch();
        });
    }).catch(GUI.fail);
};

/* ==========================================================================
   Actions
   ========================================================================== */
P.act = {snapshot: null, preview: null};

P.act.yaml = function () { return P.$('act-select').value; };

P.act.selected = function () {
    var path = P.act.yaml();
    if (path) { GUI.store('yaml-act-select', path); }
    P.$('act-summary').innerHTML = path ? P.pills(P.summaryOf(path)) : '';
    P.$('reset-preview').style.display = 'none';
    P.act.preview = null;
    P.act.updateCli();
    P.act.loadBackups();
};

P.act.browse = function () {
    P.browseYaml('act-select').then(function () { P.act.selected(); });
};

P.act.updateCli = function () {
    if (!P.path) { return; }
    var form = {yaml: P.act.yaml(),
                accept_old: P.$('reset-accept-old').checked};
    [['config_check', 'cli-config-check'], ['config_fix', 'cli-config-fix'],
     ['reset', 'cli-reset']].forEach(function (pair) {
        GUI.post('api/pogos/preview', {action: pair[0], form: form})
            .then(function (res) { GUI.setCli(pair[1], res.display ||
                                              res.error); })
            .catch(function () { return null; });
    });
};

P.act.loadBackups = function () {
    var select = P.$('act-backups');
    var path = P.act.yaml();
    if (!path) { select.innerHTML = '<option value="">(no yaml)</option>';
                 return; }
    GUI.get('api/pogos/backups', {path: path}).then(function (data) {
        select.innerHTML = data.backups.length ? data.backups.map(
            function (b) {
                return '<option value="' + GUI.esc(b.path) + '">' +
                    GUI.fmtTime(b.mtime) + ' (' + GUI.fmtAge(b.mtime) +
                    ')</option>';
            }).join('') : '<option value="">(no backups yet)</option>';
    }).catch(GUI.fail);
};

P.act.need = function () {
    if (!P.act.yaml()) { GUI.toast('Choose a yaml first', 'bad');
                         return false; }
    return true;
};

P.act.config = function (fix) {
    if (!P.act.need()) { return; }
    GUI.post('api/pogos/config', {yaml: P.act.yaml(), fix: fix})
        .then(function (res) {
            if (res.started === false || res.error) {
                GUI.toast(res.message || res.error, 'bad');
                return;
            }
            P.act.snapshot = fix ? {before: res.snapshot,
                                    after: P.act.yaml()} : null;
            GUI.toast(res.message, 'ok');
            GUI.consoles.actions.focus();
        }).catch(GUI.fail);
};

P.act.done = function (job) {
    // pogos_config (fix) finished: show what changed
    P.loadYamls();
    P.act.loadBackups();
    var snap = P.act.snapshot;
    P.act.snapshot = null;
    if (!snap || job.kind !== 'config') { return; }
    GUI.post('api/diff', {left: snap.before, right: snap.after, any: 1,
                          context: 4}).then(function (data) {
        if (data.identical) {
            GUI.toast('pogos_config made no changes to the yaml', 'ok');
            return;
        }
        GUI.showDiff({left: snap.before, right: snap.after, any: true,
                      title: 'Changes made by pogos_config',
                      leftLabel: 'before pogos_config',
                      rightLabel: 'after: ' + snap.after});
    }).catch(GUI.fail);
};

P.act.diffBackup = function () {
    var backup = P.$('act-backups').value;
    if (!backup || !P.act.yaml()) { GUI.toast('No backup chosen', 'bad');
                                    return; }
    GUI.showDiff({left: backup, right: P.act.yaml(), any: true,
                  title: 'Backup vs current', leftLabel: 'backup ' +
                  GUI.basename(backup), rightLabel: 'current ' +
                  P.act.yaml()});
};

P.act.pickDiff = function (side) {
    GUI.pickFile({title: 'Choose the ' + side + ' file', any: true,
                  start: P.$('diff-' + side).value || (P.path || '')})
        .then(function (path) { if (path) { P.$('diff-' + side).value = path;
                                            } });
};

P.act.diffFiles = function () {
    var left = P.$('diff-left').value.trim();
    var right = P.$('diff-right').value.trim();
    if (!left || !right) { GUI.toast('Choose both files', 'bad'); return; }
    GUI.showDiff({left: left, right: right, any: true,
                  title: 'Compare files'});
};

P.act.runsAction = function (kind) {
    // the actions on every run: retry all failed / stop all running /
    //   reset run records (dry run: report only)
    var spec = {
        retry: {url: 'api/pogos/retry_failed', dry: 'runs-retry-dry',
                title: 'Retry all failed', label: 'Retry',
                html: 'Run every failed / stopped / lost run again?'},
        stop: {url: 'api/pogos/stop_all', dry: 'runs-stop-dry',
               title: 'Stop all running', label: 'Stop all',
               html: 'Stop every run and command started from this gui?'},
        reset: {url: 'api/pogos/runs_reset', dry: 'runs-reset-dry',
                title: 'Reset run records', label: 'Remove records',
                html: null}
    }[kind];
    var dry = P.$(spec.dry).checked;
    var form = {dry_run: dry};
    if (kind === 'reset') {
        form.state = P.$('runs-reset-state').value;
        spec.html = 'Remove the <b>' + GUI.esc(form.state === 'all' ?
            'finished' : form.state) + '</b> run records from the Status ' +
            'and Processes tabs?';
    }
    var go = function () {
        return GUI.post(spec.url, form).then(function (res) {
            GUI.toast(res.message, res.success === false ? 'bad' : 'ok',
                      8000);
            if (kind === 'retry') {
                P.$('runs-retry-list').textContent = (res.runs || []).length ?
                    (dry ? 'Would retry: ' : 'Retried: ') +
                    res.runs.join(', ') : '';
                if (!dry && res.local) { GUI.consoles.run.focus(); }
            }
            if (!dry) { P.status.refresh(); GUI.refreshState(); }
        }).catch(GUI.fail);
    };
    if (dry) { go(); return; }
    GUI.confirm(spec.title, spec.html, spec.label).then(function (ok) {
        if (ok) { go(); }
    });
};

P.act.renderPreview = function (data) {
    var box = P.$('reset-preview');
    box.style.display = '';
    var rows = '';
    Object.keys(data.targets).forEach(function (step) {
        data.targets[step].forEach(function (target) {
            rows += '<tr><td>' + GUI.esc(step) + '</td><td>' +
                GUI.esc(target.path) + '</td><td class="num">' +
                target.nfiles + '</td><td class="num">' +
                GUI.fmtBytes(target.size) + '</td></tr>';
        });
    });
    box.innerHTML = '<h3>Reset preview: ' + GUI.esc(GUI.basename(data.yaml)) +
        '</h3>' + (data.version_ok ? '' : '<div class="notice warn">This ' +
        'yaml is from another POGOS version - tick "accept older yaml" to ' +
        'reset it.</div>') + (data.ndirs === 0 ? '<div class="notice ok">' +
        'Nothing to reset - no output / plot / temporary / other ' +
        'directories exist for this yaml.</div>' : '<p>' + data.ndirs +
        ' directories (' + data.nfiles + ' files, ' +
        GUI.fmtBytes(data.size) + ') will be deleted and recreated empty:' +
        '</p><div class="table-wrap"><table class="reset-table"><thead><tr>' +
        '<th>Step</th><th>Directory</th><th class="num">Files</th>' +
        '<th class="num">Size</th></tr></thead><tbody>' + rows +
        '</tbody></table></div>') + (data.warnings.length ? '<div ' +
        'class="notice warn">' + data.warnings.map(GUI.esc).join('<br>') +
        '</div>' : '');
};

P.act.resetPreview = function () {
    if (!P.act.need()) { return Promise.resolve(null); }
    var box = P.$('reset-preview');
    box.style.display = '';
    box.innerHTML = '<p class="muted">Working out what pogos_reset would ' +
        'delete (loads the POGOS constants - a few seconds)...</p>';
    return GUI.post('api/pogos/reset_preview', {yaml: P.act.yaml()}, 300000)
        .then(function (data) {
            P.act.preview = data;
            P.act.renderPreview(data);
            return data;
        }).catch(function (err) {
            box.innerHTML = '<div class="notice bad">' + GUI.esc(err.message) +
                '</div>';
            return null;
        });
};

P.act.reset = function () {
    if (!P.act.need()) { return; }
    var go = function (data) {
        if (!data) { return; }
        if (data.ndirs === 0) { GUI.toast('Nothing to reset', 'ok'); return; }
        GUI.confirmTyped({title: 'Reset project outputs', word: 'RESET',
                          label: 'Reset',
                          html: '<p>This permanently deletes <b>' +
                                data.ndirs + ' directories</b> (' +
                                data.nfiles + ' files, ' +
                                GUI.fmtBytes(data.size) + ') of <code>' +
                                GUI.esc(GUI.basename(data.yaml)) +
                                '</code> and recreates them empty.</p><p ' +
                                'class="muted">Raw inputs and calibration ' +
                                'files are not touched.</p>'})
            .then(function (ok) {
                if (!ok) { return; }
                GUI.startJob('api/pogos/reset', {
                    yaml: P.act.yaml(), confirm: 'RESET',
                    accept_old: P.$('reset-accept-old').checked
                }, GUI.consoles.actions);
                P.act.preview = null;
            });
    };
    if (P.act.preview && P.act.preview.yaml === P.act.yaml()) {
        go(P.act.preview);
    } else { P.act.resetPreview().then(go); }
};

/* ==========================================================================
   Status (pogos_run progress)
   ========================================================================== */
P.status = {runs: [], run: null, current: null, checked: {}, loading: false,
            open: {}, figs: {stream: null, list: []}};

// the log viewer also follows run logs ("run:{run id}")
P.baseLogUrl = GUI.logUrl;
GUI.logUrl = function (tab) {
    if (tab.id.indexOf('run:') === 0) {
        return 'api/pogos/run_log?id=' + encodeURIComponent(tab.id.substring(4)) +
            '&offset=' + tab.offset;
    }
    return P.baseLogUrl(tab);
};

P.status.init = function () {
    GUI.onTab('status', P.status.refresh);
    setInterval(function () {
        if (GUI.currentTab === 'status' && !document.hidden) {
            P.status.refresh();
        }
    }, 3000);
    P.$('status-all').onclick = function () {
        var on = this.checked;
        P.status.visible().forEach(function (run) {
            P.status.checked[run.id] = on; });
        P.status.renderRuns();
    };
};

P.status.refresh = function () {
    if (!P.path || P.status.loading) { return; }
    P.status.loading = true;
    var done = function () { P.status.loading = false; };
    if (P.status.current) {
        GUI.get('api/pogos/run', {id: P.status.current}).then(function (run) {
            P.status.run = run;
            // the streamed figures (for the Plots buttons of every step)
            return P.status.loadFigs(run).then(function () {
                done();
                P.status.renderRun();
            });
        }).catch(function (err) { done(); P.status.back(); GUI.fail(err); });
        return;
    }
    GUI.get('api/pogos/runs').then(function (data) {
        done();
        P.status.runs = data.runs;
        P.status.renderRuns();
    }).catch(function () { done(); });
};

P.status.duration = function (start, end) {
    // "3 min 20 s" from two unix times (end = now if running)
    if (!start) { return ''; }
    var sec = Math.max(0, (end || Date.now() / 1000) - start);
    if (sec < 60) { return Math.round(sec) + ' s'; }
    if (sec < 3600) { return Math.floor(sec / 60) + ' min ' +
                      Math.round(sec % 60) + ' s'; }
    return Math.floor(sec / 3600) + ' h ' + Math.round((sec % 3600) / 60) +
        ' min';
};

P.status.bar = function (done, total, detail) {
    // a small progress bar (done / total) with a detail text
    if (!total) {
        return detail ? '<span class="muted small">' + GUI.esc(detail) +
            '</span>' : '';
    }
    var pct = Math.max(0, Math.min(100, Math.round(100 * (done || 0) /
                                                   total)));
    return '<div class="pbar"><div class="pbar-fill" style="width:' + pct +
        '%"></div><span class="pbar-text">' + (done || 0) + ' / ' + total +
        '</span></div>' + (detail ? '<div class="muted small">' +
        GUI.esc(detail) + '</div>' : '');
};

P.status.visible = function () {
    // the runs that pass the active-only, flavour and text filters
    var active = P.$('status-active-only').checked;
    var flavour = P.$('status-flavour').value;
    var words = P.$('status-filter').value.toLowerCase().split(/\s+/)
        .filter(function (w) { return w; });
    return P.status.runs.filter(function (run) {
        if (active && run.status !== 'running' && run.status !== 'unknown') {
            return false;
        }
        if (flavour && (run.flavours || []).indexOf(flavour) < 0) {
            return false;
        }
        if (words.length === 0) { return true; }
        var text = [run.status, run.yaml_name, run.project, run.instmode,
                    run.current, run.error, run.host, run.slurm_job,
                    (run.flavours || []).join(' '), GUI.fmtTime(run.started)]
            .join(' ').toLowerCase();
        return words.every(function (w) { return text.indexOf(w) >= 0; });
    });
};

P.status.fillFlavours = function () {
    // the flavour dropdown: every flavour seen in the runs (keeps the pick)
    var sel = P.$('status-flavour');
    var seen = {};
    P.status.runs.forEach(function (run) {
        (run.flavours || []).forEach(function (f) { seen[f] = true; });
    });
    var cur = sel.value;
    if (cur) { seen[cur] = true; }
    var names = Object.keys(seen).sort();
    var key = names.join('|');
    if (sel.getAttribute('data-key') === key) { return; }
    sel.setAttribute('data-key', key);
    sel.innerHTML = '<option value="">All flavours</option>' +
        names.map(function (f) {
            return '<option value="' + GUI.esc(f) + '">' + GUI.esc(f) +
                '</option>'; }).join('');
    sel.value = cur;
};

P.status.renderRuns = function () {
    P.$('status-runs-view').style.display = '';
    P.$('status-run-view').style.display = 'none';
    var body = P.$('status-runs');
    P.status.fillFlavours();
    var runs = P.status.visible();
    var nrun = P.status.runs.filter(function (r) {
        return r.status === 'running'; }).length;
    P.$('status-note').textContent = P.status.runs.length + ' run(s), ' +
        nrun + ' running' + (runs.length < P.status.runs.length ? ', ' +
        runs.length + ' shown' : '');
    if (runs.length === 0 && P.status.runs.length > 0) {
        body.innerHTML = '<tr><td colspan="10" class="muted">No runs ' +
            'match the filters.</td></tr>';
        return;
    }
    if (runs.length === 0) {
        body.innerHTML = '<tr><td colspan="10" class="muted">No runs ' +
            'recorded yet - start one on the Run tab (runs from a ' +
            'terminal or batch job appear here too).</td></tr>';
        return;
    }
    body.innerHTML = runs.map(function (run) {
        return '<tr class="clickable" data-id="' + GUI.esc(run.id) + '">' +
            '<td><input type="checkbox"' + (P.status.checked[run.id] ?
            ' checked' : '') + '></td><td><span class="badge ' +
            GUI.esc(run.status) + '">' + GUI.esc(run.status) + '</span></td>' +
            '<td class="nowrap small">' + GUI.fmtTime(run.started) + '</td>' +
            '<td class="mono small">' + GUI.esc(run.yaml_name) + '</td>' +
            '<td class="small">' + GUI.esc(run.project) + '</td>' +
            '<td class="small">' + GUI.esc(run.instmode) + '</td>' +
            '<td style="min-width:120px">' + P.status.bar(run.ndone,
            run.nstages, 'stages') + '</td><td class="small">' +
            GUI.esc(run.current || (run.error ? run.error : '')) +
            '</td><td class="nowrap small">' + P.status.duration(
                run.started, run.ended) + '</td><td class="small">' +
            GUI.esc(run.slurm_job ? 'slurm ' + run.slurm_job :
                    run.host + ' pid ' + run.pid) + '</td></tr>';
    }).join('');
    body.querySelectorAll('tr').forEach(function (tr) {
        var id = tr.getAttribute('data-id');
        tr.querySelector('input').onclick = function (ev) {
            ev.stopPropagation();
            P.status.checked[id] = this.checked;
        };
        tr.onclick = function () { P.status.show(id); };
    });
};

P.status.show = function (id) {
    P.status.current = id;
    P.status.open = {};
    P.status.run = null;
    P.status.figs = {stream: null, list: []};
    P.$('status-runs-view').style.display = 'none';
    P.$('status-run-view').style.display = '';
    P.$('status-steps').innerHTML = '<tr><td colspan="7" class="muted">' +
        'Loading...</td></tr>';
    P.status.refresh();
};

P.status.back = function () {
    P.status.current = null;
    P.status.run = null;
    P.status.refresh();
};

P.status.openLog = function (search) {
    // open the run log (optionally at a step marker)
    var run = P.status.run;
    GUI.openLog('run:' + run.id, {label: 'run: ' + run.yaml_name,
                                  subtitle: run.project,
                                  search: search || null});
};

P.status.nodeKey = function (stage, path) {
    // a stable key of a tree row (for the expand / collapse state)
    return stage.level + '|' + stage.flavour + '|' + path.join('␟');
};

P.status.isOpen = function (stage, node) {
    // rows are open unless the user closed them; finished branches start
    //   closed (the running path and pending steps stay visible)
    var key = P.status.nodeKey(stage, node.path || []);
    if (P.status.open[key] !== undefined) { return P.status.open[key]; }
    return ['complete', 'not run'].indexOf(node.status) < 0;
};

P.status.stepProgress = function (node) {
    // the progress cell: reported done / total, else the finished leaf
    //   steps below it
    if (node.total || node.done !== null && node.done !== undefined) {
        return P.status.bar(node.done, node.total, node.detail);
    }
    if (node.leaves_total) {
        return P.status.bar(node.leaves_done, node.leaves_total, null);
    }
    // only a detail text (e.g. which file is being downloaded)
    if (node.detail && node.status === 'running') {
        return P.status.bar(null, null, node.detail);
    }
    return '';
};

P.status.treeRows = function (stage, nodes, depth, rows) {
    // one row per step (children indented below their parent)
    nodes.forEach(function (node) {
        var hasKids = node.children && node.children.length > 0;
        var open = hasKids && P.status.isOpen(stage, node);
        var key = P.status.nodeKey(stage, node.path);
        var marker = 'POGOS PROGRESS | ' + stage.level + ' | ' +
            stage.flavour + ' | ' + node.path.join(' / ');
        var started = node.status !== 'pending' && node.status !== 'not run';
        P.status.rowNodes.push({stage: stage, node: node, marker: started ?
                                marker : null});
        rows.push('<tr class="status-row st-step ' + GUI.esc(node.status) +
            '"><td><span class="st-name" ' +
            'style="padding-left:' + (depth * 20 + 6) + 'px">' + (hasKids ?
            '<span class="st-toggle" data-key="' + GUI.esc(key) + '">' +
            (open ? '&#9662;' : '&#9656;') + '</span>' : '<span ' +
            'class="st-toggle-space"></span>') + (node.item ? '<span ' +
            'class="st-item">' + GUI.esc(node.name) + '</span>' :
            GUI.esc(node.name)) + (node.loop ? ' <span class="muted ' +
            'small">(' + (node.children.length ? node.children.length +
            ' item(s)' : 'items not known yet') + ')</span>' : '') +
            (node.error ? '<div class="small st-error">' +
             GUI.esc(node.error) + '</div>' : '') + '</span></td>' +
            '<td class="nowrap small">' + GUI.fmtTime(node.started) +
            '</td><td class="nowrap small">' + (node.started ?
            P.status.duration(node.started, node.ended) : '') + '</td>' +
            '<td><span class="badge ' + GUI.esc(node.status) + '">' +
            GUI.esc(node.status) + '</span></td><td style="min-width:180px">' +
            P.status.stepProgress(node) + '</td>' + P.status.actionsCell(
                P.status.rowNodes.length - 1, started, node) + '</tr>');
        if (open) { P.status.treeRows(stage, node.children, depth + 1, rows); }
    });
};

P.status.renderRun = function () {
    var run = P.status.run;
    if (!run) { return; }
    var head = P.$('status-run-head');
    head.innerHTML = '<div class="status-head-row"><button ' +
        'id="status-back">&larr; All runs</button><span class="badge ' +
        GUI.esc(run.status) + '">' + GUI.esc(run.status) + '</span><b ' +
        'class="mono">' + GUI.esc(run.yaml_name) + '</b><span ' +
        'class="muted small">' + GUI.esc(run.project) + ' &middot; ' +
        GUI.esc(run.instmode) + ' &middot; started ' +
        GUI.fmtTime(run.started) + ' &middot; ' +
        P.status.duration(run.started, run.ended) + ' &middot; ' +
        GUI.esc(run.slurm_job ? 'slurm ' + run.slurm_job : run.host +
                ' pid ' + run.pid) + '</span><span class="grow"></span>' +
        '<button id="status-expand">Expand all</button><button ' +
        'id="status-collapse">Collapse finished</button><button ' +
        'id="status-log"' + (run.log ? '' : ' disabled title="no ' +
        'log recorded (run started outside the gui)"') + '>Open log' +
        '</button>' + (run.plot_stream ? '<button id="status-plots">' +
        'Streamed plots</button>' : '') + '</div>' + (run.error ?
        '<div class="notice bad">' + GUI.esc(run.error) + '</div>' : '') +
        (run.current ? '<div class="small st-now">Now: <b>' +
         GUI.esc(run.current) + '</b></div>' : '');
    P.$('status-back').onclick = P.status.back;
    P.$('status-log').onclick = function () { P.status.openLog(null); };
    P.$('status-expand').onclick = function () { P.status.setAll(true); };
    P.$('status-collapse').onclick = function () {
        P.status.open = {};
        P.status.renderRun();
    };
    if (P.$('status-plots')) {
        P.$('status-plots').onclick = function () {
            P.stream.show(GUI.basename(run.plot_stream));
        };
    }
    var rows = [];
    var lastLevel = null;
    // the stage / step of every row (for the row buttons)
    P.status.rowNodes = [];
    run.steps.forEach(function (stage) {
        // a band per reduction level, a header row per flavour
        if (stage.level !== lastLevel) {
            rows.push('<tr class="st-level-row"><td colspan="6">' +
                      GUI.esc(stage.level) + '</td></tr>');
            lastLevel = stage.level;
        }
        P.status.rowNodes.push({stage: stage, node: null, marker:
            stage.started ? 'POGOS PROGRESS | ' + stage.level + ' | ' +
            stage.flavour + ' | start' : null});
        var stageRow = P.status.rowNodes.length - 1;
        rows.push('<tr class="status-row st-flavour-row ' +
            GUI.esc(stage.status) + '"><td><b>' +
            GUI.esc(stage.flavour) + '</b>' + (stage.error ? '<div ' +
            'class="small st-error">' + GUI.esc(stage.error) + '</div>' :
            '') + (stage.children.length ? '' : ' <span class="muted ' +
            'small">' + (stage.status === 'pending' &&
            run.status === 'running' ? '(its steps are listed once the ' +
            'preamble has planned them)' : '(no steps declared for this ' +
            'flavour)') + '</span>') +
            '</td><td class="nowrap small">' + GUI.fmtTime(stage.started) +
            '</td><td class="nowrap small">' + (stage.started ?
            P.status.duration(stage.started, stage.ended) : '') + '</td>' +
            '<td><span class="badge ' + GUI.esc(stage.status) + '">' +
            GUI.esc(stage.status) + '</span></td><td style="min-width:' +
            '180px">' + (stage.leaves_total ? P.status.bar(
                stage.leaves_done, stage.leaves_total, null) : '') +
            '</td>' + P.status.actionsCell(stageRow, !!stage.started, null) +
            '</tr>');
        P.status.treeRows(stage, stage.children, 1, rows);
    });
    var body = P.$('status-steps');
    body.innerHTML = rows.join('') || '<tr><td colspan="6" ' +
        'class="muted">No stages planned.</td></tr>';
    body.querySelectorAll('.st-toggle').forEach(function (el) {
        el.onclick = function (ev) {
            ev.stopPropagation();
            var key = el.getAttribute('data-key');
            var open = el.innerHTML.charCodeAt(0) === 9662;
            P.status.open[key] = !open;
            P.status.renderRun();
        };
    });
    body.querySelectorAll('[data-row-act]').forEach(function (btn) {
        btn.onclick = function (ev) {
            ev.stopPropagation();
            var row = P.status.rowNodes[Number(btn.getAttribute('data-row'))];
            var act = btn.getAttribute('data-row-act');
            if (act === 'log') {
                if (!run.log) {
                    GUI.toast('No log recorded for this run', 'bad');
                    return;
                }
                P.status.openLog(row.marker);
            } else if (act === 'code') {
                P.status.showCode(row.stage, row.node);
            } else if (act === 'doc') {
                P.status.showDoc(row.stage, row.node);
            } else if (act === 'plots') {
                P.status.showPlots(row.stage, row.node);
            }
        };
    });
};

P.status.actionsCell = function (index, started, node) {
    // the Log / Code / Doc buttons of one row (only those that apply)
    var btn = function (act, label, title) {
        return '<button class="small" data-row-act="' + act + '" ' +
            'data-row="' + index + '" title="' + GUI.esc(title) + '">' +
            label + '</button>';
    };
    // a missing button keeps its slot (the columns stay aligned)
    var none = function (label) {
        return '<button class="small st-slot" disabled>' + label +
            '</button>';
    };
    var html = (started ? btn('log', 'Log', 'Open the log at this step') :
                none('Log')) +
        (node && (node.src_file || node.func) ?
         btn('code', 'Code', 'The code of this step') : none('Code')) +
        (node && (node.desc || node.func) ?
         btn('doc', 'Doc', 'What this step does') : none('Doc')) +
        P.status.plotsButton(index);
    return '<td class="st-actions nowrap">' + html + '</td>';
};

/* ---- the figures of a step (Plots buttons) ---- */
P.status.loadFigs = function (run) {
    // fetch the figures this run streamed (only the new ones)
    var figs = P.status.figs;
    var name = run.plot_stream ? GUI.basename(run.plot_stream) : null;
    if (name !== figs.stream) {
        P.status.figs = figs = {stream: name, list: []};
    }
    if (!name) { return Promise.resolve(); }
    return GUI.get('api/pogos/stream', {name: name, since: figs.list.length})
        .then(function (res) {
            if (res.name === P.status.figs.stream) {
                P.status.figs.list = P.status.figs.list.concat(res.figures);
            }
        }).catch(function () { return null; });
};

P.status.figsOf = function (stage, node) {
    // the figures shown inside a stage (node null) or a step and the
    //   steps below it (the figure's step path starts with the node path)
    var path = node ? node.path : [];
    return P.status.figs.list.filter(function (fig) {
        var step = fig.step;
        if (!fig.path || !step || step.level !== stage.level ||
            step.flavour !== stage.flavour) { return false; }
        var fpath = step.path || [];
        if (fpath.length < path.length) { return false; }
        for (var i = 0; i < path.length; i++) {
            if (String(fpath[i]) !== String(path[i])) { return false; }
        }
        return true;
    });
};

P.status.plotsButton = function (index) {
    // Plots: active with figures; light grey while they may still come
    //   (pending / running); dark grey once the step ended without any
    var row = P.status.rowNodes[index];
    var run = P.status.run;
    if (!row || !run) { return ''; }
    var count = P.status.figsOf(row.stage, row.node).length;
    if (count > 0) {
        return '<button class="small st-plots" data-row-act="plots" ' +
            'data-row="' + index + '" title="The ' + count + ' figure(s) ' +
            'shown in this ' + (row.node ? 'step' : 'stage') + '">Plots (' +
            count + ')</button>';
    }
    var item = row.node || row.stage;
    var open = run.status === 'running' &&
        ['pending', 'running'].indexOf(item.status) >= 0;
    var title = !run.plot_stream ? 'Figures were not streamed (the run ' +
        'was not started from the gui)' : open ? 'No figures yet - ' +
        'they appear here as this step shows them' : 'No figures were ' +
        'shown in this ' + (row.node ? 'step' : 'stage');
    return '<button class="small st-plots ' + (open && run.plot_stream ?
        'st-plots-wait' : 'st-plots-none') + '" disabled title="' +
        GUI.esc(title) + '">Plots</button>';
};

P.status.showPlots = function (stage, node) {
    // an overlay with the figures of a stage / step (click: full size,
    //   zoom / pan for interactive figures)
    var figures = P.status.figsOf(stage, node);
    var label = [stage.level, stage.flavour].concat(node ? node.path : [])
        .join(' / ');
    var items = figures.map(P.stream.lbItem);
    var body = '<div class="plots-gallery small st-plots-gallery">' +
        figures.map(function (fig, index) {
            var where = (fig.step && fig.step.path || []).slice(
                node ? node.path.length : 0).join(' / ');
            return '<div class="plot-card" data-index="' + index + '"><img ' +
                'loading="lazy" src="' + GUI.rawUrl(fig.path) + '" alt="">' +
                '<div class="pc-title">' + GUI.esc(fig.title || fig.file) +
                '</div>' + (where ? '<div class="pc-name">' +
                GUI.esc(where) + '</div>' : '') + '<div class="pc-meta">#' +
                (fig.number || '') + ' &middot; ' + GUI.fmtTime(fig.time) +
                (fig.figure ? ' &middot; zoom / pan' : '') + '</div></div>';
        }).join('') + '</div>';
    var dlg = GUI.dialog({id: 'status-plots-dlg', wide: true,
                          title: 'Plots: ' + label, body: body});
    dlg.querySelectorAll('.plot-card').forEach(function (card) {
        card.onclick = function () {
            GUI.lightbox(items, Number(card.getAttribute('data-index')));
        };
    });
};

P.status.codeHtml = function (data, mark) {
    // numbered source lines (mark: the line to highlight)
    if (data.error) {
        return '<div class="notice warn small">' + GUI.esc(data.error) +
            '</div>';
    }
    return '<div class="code-path mono small">' + GUI.esc(data.file) + ':' +
        data.line + ' <button class="small" data-copy="' +
        GUI.esc(data.file + ':' + data.line) + '">Copy</button></div>' +
        '<pre class="code-view">' + data.lines.map(function (pair) {
            return '<span class="code-line' + (pair[0] === mark ?
                ' mark' : '') + '"><span class="code-no">' + pair[0] +
                '</span>' + P.status.pyHtml(pair[1]) + '</span>';
        }).join('') + '</pre>';
};

P.status.pyHtml = function (text) {
    // a light python highlight: comments, strings and keywords
    var out = '';
    var rest = text;
    var re = /(#.*$)|('''|"""|'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")|\b(def|class|return|if|elif|else|for|while|in|not|and|or|import|from|as|with|try|except|finally|raise|yield|lambda|None|True|False|self)\b/g;
    var last = 0;
    var match;
    while ((match = re.exec(rest)) !== null) {
        out += GUI.esc(rest.substring(last, match.index));
        var cls = match[1] ? 'c' : (match[2] ? 's' : 'k');
        out += '<span class="py-' + cls + '">' + GUI.esc(match[0]) +
            '</span>';
        last = match.index + match[0].length;
        if (match[0].length === 0) { re.lastIndex++; }
    }
    return out + GUI.esc(rest.substring(last));
};

P.status.wireCopy = function (box) {
    box.querySelectorAll('[data-copy]').forEach(function (btn) {
        btn.onclick = function () {
            GUI.copyText(btn.getAttribute('data-copy'), btn);
        };
    });
};

P.status.showCode = function (stage, node) {
    // where the step is marked in the code and the function doing it
    var parts = [];
    if (node.src_file) {
        parts.push({title: 'Where this step starts', id: 'code-src',
                    url: 'api/code', args: {file: node.src_file,
                                            line: node.src_line},
                    mark: node.src_line});
    }
    if (node.func) {
        parts.push({title: 'Function: ' + node.func, id: 'code-func',
                    url: 'api/code', args: {func: node.func}});
    }
    var body = parts.map(function (part) {
        return '<h3>' + GUI.esc(part.title) + '</h3><div id="' + part.id +
            '"><p class="muted">Loading...</p></div>';
    }).join('');
    GUI.dialog({id: 'status-code', wide: true, title: 'Code: ' +
                [stage.flavour].concat(node.path).join(' / '), body: body,
                buttons: [{label: 'Close'}]});
    parts.forEach(function (part) {
        GUI.get(part.url, part.args).then(function (data) {
            var box = P.$(part.id);
            box.innerHTML = P.status.codeHtml(data, part.mark || data.line);
            P.status.wireCopy(box);
            var marked = box.querySelector('.code-line.mark');
            if (marked && part.id === 'code-src') {
                marked.scrollIntoView({block: 'nearest'});
            }
        }).catch(function (err) {
            P.$(part.id).innerHTML = '<div class="notice bad">' +
                GUI.esc(err.message) + '</div>';
        });
    });
};

P.status.showDoc = function (stage, node) {
    // the step description (XXXX_DESC) or the docstring of XXXX_FUNC
    var title = [stage.flavour].concat(node.path).join(' / ');
    var head = '<div class="muted small">' + GUI.esc(stage.level) + ' / ' +
        GUI.esc(title) + '</div>' + (node.func ? '<div class="mono small" ' +
        'style="margin:4px 0">' + GUI.esc(node.func) + '</div>' : '');
    var show = function (text, source) {
        return head + (source ? '<div class="muted small">' + source +
            '</div>' : '') + '<pre class="doc-text">' + GUI.esc(text) +
            '</pre>';
    };
    if (node.desc) {
        GUI.dialog({id: 'status-doc', title: 'Doc: ' + node.name,
                    body: show(node.desc, null), buttons: [{label: 'Close'}]});
        return;
    }
    GUI.dialog({id: 'status-doc', title: 'Doc: ' + node.name,
                body: head + '<p class="muted">Loading...</p>',
                buttons: [{label: 'Close'}]});
    GUI.get('api/code', {func: node.func}).then(function (data) {
        var box = document.querySelector('#status-doc .gui-dialog-body');
        box.innerHTML = data.error ? head + '<div class="notice warn ' +
            'small">' + GUI.esc(data.error) + '</div>' : show(data.doc ||
            '(no docstring)', 'From the docstring of the function (no ' +
            'description written for this step):');
    }).catch(GUI.fail);
};

P.status.setAll = function (open) {
    // open (or close) every row with children
    var walk = function (stage, nodes) {
        nodes.forEach(function (node) {
            if (node.children.length) {
                P.status.open[P.status.nodeKey(stage, node.path)] = open;
                walk(stage, node.children);
            }
        });
    };
    (P.status.run ? P.status.run.steps : []).forEach(function (stage) {
        walk(stage, stage.children);
    });
    P.status.renderRun();
};

P.status.removeSelected = function () {
    var ids = Object.keys(P.status.checked).filter(function (id) {
        return P.status.checked[id]; });
    if (ids.length === 0) { GUI.toast('Select runs first'); return; }
    GUI.post('api/pogos/run_remove', {ids: ids}).then(function (res) {
        GUI.toast(res.message, 'ok');
        P.status.checked = {};
        P.status.refresh();
    }).catch(GUI.fail);
};

/* ==========================================================================
   Plot stream (figures runs show, streamed instead of plot windows)
   ========================================================================== */
P.stream = {streams: [], name: null, figures: [], loading: false};

P.stream.init = function () {
    P.$('stream-size').onchange = P.stream.renderGallery;
    GUI.onTab('plots', function () {
        if (P.stream.active()) { P.stream.refresh(); }
        else { P.plots.refresh(); }
    });
    GUI.onTab('plotstab:stream', P.stream.refresh);
    GUI.onTab('plotstab:disk', P.plots.refresh);
    setInterval(function () {
        if (GUI.currentTab === 'plots' && P.stream.active() &&
            !document.hidden) { P.stream.refresh(); }
    }, 3000);
    GUI.setSubTab('plotstab', GUI.recall('subtab-plotstab', 'stream'));
};

P.stream.active = function () {
    return P.$('plotstab-stream').classList.contains('active');
};

P.stream.show = function (name) {
    // open one stream (e.g. from the Status tab)
    P.$('stream-follow').checked = false;
    P.stream.select(name);
    GUI.setTab('plots');
    GUI.setSubTab('plotstab', 'stream');
};

P.stream.select = function (name) {
    if (name !== P.stream.name) {
        P.stream.name = name;
        P.stream.figures = [];
        P.stream.renderGallery();
    }
    P.stream.refresh();
};

P.stream.refresh = function () {
    if (!P.path || P.stream.loading) { return; }
    P.stream.loading = true;
    GUI.get('api/pogos/streams').then(function (data) {
        P.stream.streams = data.streams;
        if (P.$('stream-follow').checked && data.streams.length &&
            data.streams[0].name !== P.stream.name) {
            P.stream.name = data.streams[0].name;
            P.stream.figures = [];
        }
        P.stream.renderList();
        if (!P.stream.name) { P.stream.loading = false;
                              P.stream.renderGallery(); return; }
        return GUI.get('api/pogos/stream', {name: P.stream.name,
                                            since: P.stream.figures.length})
            .then(function (res) {
                if (res.name === P.stream.name && res.figures.length) {
                    P.stream.figures = P.stream.figures.concat(res.figures);
                    P.stream.renderGallery();
                } else if (!P.stream.figures.length) {
                    P.stream.renderGallery();
                }
                P.stream.loading = false;
            });
    }).catch(function () { P.stream.loading = false; });
};

P.stream.renderList = function () {
    var holder = P.$('stream-list');
    if (P.stream.streams.length === 0) {
        holder.innerHTML = '<p class="muted small">No streamed plots yet - ' +
            'figures of runs started from the Run tab appear here.</p>';
        return;
    }
    holder.innerHTML = P.stream.streams.map(function (st) {
        return '<div class="pt-node' + (st.name === P.stream.name ?
            ' active' : '') + '" data-name="' + GUI.esc(st.name) + '"><span ' +
            'class="pt-name" title="' + GUI.esc(st.yaml || st.name) + '">' +
            GUI.esc(GUI.basename(st.yaml || st.name)) + '<br><span ' +
            'class="pt-count">' + GUI.fmtTime(st.started) + ' &middot; ' +
            GUI.esc(st.kind || '') + '</span></span><span class="pt-count">' +
            st.count + '</span></div>';
    }).join('');
    holder.querySelectorAll('[data-name]').forEach(function (el) {
        el.onclick = function () {
            P.$('stream-follow').checked = false;
            P.stream.select(el.getAttribute('data-name'));
        };
    });
};

P.stream.renderGallery = function () {
    var gallery = P.$('stream-gallery');
    gallery.className = 'plots-gallery ' + P.$('stream-size').value;
    var figures = P.stream.figures.filter(function (f) { return f.path; })
        .slice().reverse();
    P.$('stream-note').textContent = P.stream.name ? figures.length +
        ' figure(s), newest first' : '';
    if (figures.length === 0) {
        gallery.innerHTML = '<div class="plots-empty">' + (P.stream.name ?
            'No figures yet - they appear here as the run shows them.' :
            'Choose a stream on the left.') + '</div>';
        return;
    }
    gallery.innerHTML = figures.map(function (fig, index) {
        return '<div class="plot-card" data-index="' + index + '"><img ' +
            'loading="lazy" src="' + GUI.rawUrl(fig.path) + '" alt="">' +
            '<div class="pc-title">' + GUI.esc(fig.title || fig.file) +
            '</div>' + (fig.name ? '<div class="pc-name">' +
            GUI.esc(fig.name) + '</div>' : '') + '<div class="pc-meta">#' + (fig.number || '') + ' &middot; ' +
            GUI.fmtTime(fig.time) + '</div></div>';
    }).join('');
    var items = figures.map(P.stream.lbItem);
    gallery.querySelectorAll('.plot-card').forEach(function (card) {
        card.onclick = function () {
            GUI.lightbox(items, Number(card.getAttribute('data-index')));
        };
    });
};

P.stream.lbItem = function (fig) {
    // a streamed figure as a lightbox item (interactive when pickled)
    var details = [['Figure', '#' + (fig.number || '') + ' - ' +
                    GUI.fmtTime(fig.time)]];
    if (fig.step && (fig.step.level || (fig.step.path || []).length)) {
        details.push(['Step', [fig.step.level, fig.step.flavour]
            .concat(fig.step.path || []).filter(function (part) {
                return part; }).join(' / ')]);
    }
    if (fig.name) { details.push(['Plot name', fig.name]); }
    if (fig.func) { details.push(['Function', fig.func]); }
    if (!fig.figure && fig.static_reason) {
        details.push(['Not interactive', fig.static_reason]);
    }
    return {path: fig.path, name: fig.title || fig.file,
            title: fig.title || fig.file, figure: fig.figure_path || null,
            description: fig.description, details: details,
            info: (fig.title || '') + ' - ' + GUI.fmtTime(fig.time) +
                (fig.figure_path ? '   |   interactive: matplotlib ' +
                 'toolbar (zoom / pan / home), keys inside the figure ' +
                 'are matplotlib\'s' : '')};
};

P.stream.removeCurrent = function () {
    if (!P.stream.name) { return; }
    GUI.confirm('Delete stream', 'Delete the streamed figures of <code>' +
                GUI.esc(P.stream.name) + '</code>?', 'Delete')
        .then(function (ok) {
            if (!ok) { return; }
            GUI.post('api/pogos/stream_remove', {names: [P.stream.name]})
                .then(function (res) {
                    GUI.toast(res.message, res.success ? 'ok' : 'bad');
                    P.stream.name = null;
                    P.stream.figures = [];
                    P.stream.refresh();
                }).catch(GUI.fail);
        });
};

/* ==========================================================================
   Plots
   ========================================================================== */
P.plots = {data: null, sel: {project: null, module: null}, loading: false};

P.plots.init = function () {
    P.$('plots-filter').oninput = P.debounce(P.plots.render, 200);
    P.$('plots-sort').onchange = P.plots.render;
    P.$('plots-size').onchange = function () {
        GUI.store('plots-size', this.value);
        P.plots.render();
    };
    P.$('plots-size').value = GUI.recall('plots-size', 'medium');
    P.$('plots-project').onchange = function () {
        P.plots.select(this.value || null, null);
    };
    P.$('plots-module').onchange = function () {
        P.plots.select(P.plots.sel.project, this.value || null);
    };
    P.plots.sel = GUI.recall('plots-sel', {project: null, module: null});
    setInterval(function () {
        if (GUI.currentTab === 'plots' && P.$('plots-auto').checked &&
            !P.stream.active() && !document.hidden) { P.plots.refresh(); }
    }, 15000);
};

P.plots.seen = function () { return GUI.recall('plots-seen-' + P.path, 0); };

P.plots.markSeen = function () {
    GUI.store('plots-seen-' + P.path, Date.now() / 1000);
    P.plots.render();
};

P.plots.refresh = function () {
    if (!P.path || P.plots.loading) { return; }
    P.plots.loading = true;
    GUI.get('api/pogos/plots').then(function (data) {
        P.plots.loading = false;
        var before = P.plots.data ? P.plots.data.total + ':' +
            P.plots.data.newest : null;
        P.plots.data = data;
        if (before !== data.total + ':' + data.newest) { P.plots.render(); }
    }).catch(function (err) { P.plots.loading = false; GUI.fail(err); });
};

P.plots.images = function () {
    // every image with its project / module (flavour) / dir
    var out = [];
    (P.plots.data ? P.plots.data.projects : []).forEach(function (proj) {
        proj.modules.forEach(function (mod) {
            mod.dirs.forEach(function (dir) {
                dir.images.forEach(function (img) {
                    out.push({path: img.path, name: img.name,
                              mtime: img.mtime, size: img.size,
                              title: img.title,
                              description: img.description,
                              func: img.func, project: proj.name,
                              module: mod.name, dir: dir.dir});
                });
            });
        });
    });
    return out;
};

P.plots.select = function (project, module) {
    P.plots.sel = {project: project, module: module};
    GUI.store('plots-sel', P.plots.sel);
    P.plots.render();
};

P.plots.renderPickers = function (all, seen) {
    // project dropdown, then the flavours (modules) of that project
    var projects = P.plots.data.projects;
    var sel = P.plots.sel;
    var proj = projects.filter(function (p) { return p.name === sel.project; })[0];
    if (!proj && projects.length) {
        // default: the project with the newest plot
        var newest = all.slice().sort(function (a, b) {
            return b.mtime - a.mtime; })[0];
        proj = projects.filter(function (p) {
            return newest && p.name === newest.project; })[0] || projects[0];
        sel.project = proj.name;
        sel.module = null;
    }
    if (proj && sel.module && !proj.modules.some(function (m) {
        return m.name === sel.module; })) { sel.module = null; }
    var label = function (items) {
        var fresh = items.filter(function (i) { return i.mtime > seen; })
            .length;
        return ' (' + items.length + (fresh ? ', ' + fresh + ' new' : '') +
            ')';
    };
    var psel = P.$('plots-project');
    psel.innerHTML = projects.length ? projects.map(function (p) {
        return '<option value="' + GUI.esc(p.name) + '"' + (proj &&
            p.name === proj.name ? ' selected' : '') + '>' +
            GUI.esc(p.name) + label(all.filter(function (i) {
                return i.project === p.name; })) + '</option>';
    }).join('') : '<option value="">(no projects with plots)</option>';
    var msel = P.$('plots-module');
    var mods = proj ? proj.modules : [];
    msel.innerHTML = '<option value="">All flavours' + (proj ? label(
        all.filter(function (i) { return i.project === proj.name; })) :
        '') + '</option>' + mods.map(function (m) {
            return '<option value="' + GUI.esc(m.name) + '"' +
                (m.name === sel.module ? ' selected' : '') + '>' +
                GUI.esc(m.name) + label(all.filter(function (i) {
                    return i.project === proj.name && i.module === m.name;
                })) + '</option>';
        }).join('');
    msel.disabled = mods.length === 0;
    P.$('plots-pick-note').textContent = projects.length ? projects.length +
        ' project(s) with plots' : '';
};

P.plots.render = function () {
    var gallery = P.$('plots-gallery');
    if (!P.plots.data) { gallery.innerHTML = ''; return; }
    var all = P.plots.images();
    var seen = P.plots.seen();
    P.plots.renderPickers(all, seen);
    var sel = P.plots.sel;
    var filter = P.$('plots-filter').value.toLowerCase();
    var inSel = all.filter(function (i) {
        return i.project === sel.project &&
            (!sel.module || i.module === sel.module);
    });
    var items = inSel.filter(function (i) {
        return !filter || [i.name, i.dir, i.title, i.description].join(' ')
            .toLowerCase().indexOf(filter) >= 0;
    });
    var sort = P.$('plots-sort').value;
    if (sort === 'new') { items.sort(function (a, b) {
        return b.mtime - a.mtime; }); }
    else if (sort === 'old') { items.sort(function (a, b) {
        return a.mtime - b.mtime; }); }
    gallery.className = 'plots-gallery ' + P.$('plots-size').value;
    P.$('plots-note').textContent = items.length + ' of ' + inSel.length +
        ' plot(s)' + (P.plots.data.newest ? ' - newest (any project) ' +
                      GUI.fmtAge(P.plots.data.newest) : '');
    if (items.length === 0) {
        gallery.innerHTML = '<div class="plots-empty">' + (inSel.length ?
            'No plots match.' : 'No plots yet - they appear here while ' +
            'POGOS runs.') + '</div>';
        return;
    }
    var html = '';
    var lastGroup = null;
    items.forEach(function (img, index) {
        // group by flavour / sub directory (the project is the dropdown)
        var group = img.module + (img.dir ? ' / ' + img.dir : '');
        if (sort === 'name' && group !== lastGroup) {
            html += '<div class="plots-dir">' + GUI.esc(group) + '</div>';
            lastGroup = group;
        }
        html += '<div class="plot-card" data-index="' + index + '"><img ' +
            'loading="lazy" src="' + GUI.rawUrl(img.path, '&t=' +
                                                Math.round(img.mtime)) +
            '" alt="">' + (img.title ? '<div class="pc-title">' +
            GUI.esc(img.title) + '</div>' : '') + '<div class="pc-name">' +
            GUI.esc(img.name) + '</div>' + '<div class="pc-meta">' +
            GUI.esc(sort === 'name' ? '' : group + ' - ') +
            GUI.fmtTime(img.mtime) + ' - ' + GUI.fmtBytes(img.size) +
            '</div>' + (img.mtime > seen ? '<span class="pill warn ' +
            'pc-new">new</span>' : '') + '</div>';
    });
    gallery.innerHTML = html;
    var lbItems = items.map(function (img) {
        var details = [['File', img.name],
                       ['Project / flavour', img.project + ' / ' +
                        img.module + (img.dir ? ' / ' + img.dir : '')],
                       ['Saved', GUI.fmtTime(img.mtime)]];
        if (img.func) { details.push(['Function', img.func]); }
        return {path: img.path, name: img.name,
                title: img.title || img.name,
                description: img.description, details: details,
                info: img.project + ' / ' + img.module + ' - ' +
                      GUI.fmtTime(img.mtime)};
    });
    gallery.querySelectorAll('.plot-card').forEach(function (card) {
        card.onclick = function () {
            GUI.lightbox(lbItems, Number(card.getAttribute('data-index')));
        };
    });
};

/* ==========================================================================
   Project manager (Files tab)
   ========================================================================== */
P.files = {root: null, rootLabel: '', project: null, dir: null, data: null,
           projects: null, checked: {}, sort: {key: 'name', asc: true},
           stats: {}, view: 'home', downloads: null, dlChecked: {},
           dlSort: {key: 'downloaded', asc: false}};

P.files.init = function () {
    GUI.onTab('files', P.files.refresh);
    P.$('files-filter').oninput = P.debounce(P.files.render, 150);
    P.$('pm-filter').oninput = P.debounce(function () {
        if (P.files.view === 'downloads') { P.files.renderDownloads(); }
        else { P.files.renderProjects(); }
    }, 120);
    document.querySelectorAll('#tab-files th[data-sort]').forEach(function (th) {
        th.onclick = function () {
            var key = th.getAttribute('data-sort');
            P.files.sort = {key: key, asc: P.files.sort.key === key ?
                            !P.files.sort.asc : true};
            P.files.render();
        };
    });
    document.querySelectorAll('#tab-files th[data-dlsort]').forEach(
        function (th) {
            th.onclick = function () {
                var key = th.getAttribute('data-dlsort');
                P.files.dlSort = {key: key, asc: P.files.dlSort.key === key ?
                                  !P.files.dlSort.asc : true};
                P.files.renderDownloads();
            };
        });
    // the home page cards open their page
    document.querySelectorAll('#pm-home .pm-card').forEach(function (card) {
        var open = function () {
            P.files.openView(card.getAttribute('data-view'));
        };
        card.onclick = open;
        card.onkeydown = function (ev) {
            if (ev.key === 'Enter' || ev.key === ' ') { open(); }
        };
    });
    GUI.onDataChange(function () {
        if (GUI.currentTab === 'files') { P.files.refresh(); }
    });
};

P.files.refresh = function () {
    if (!P.path) { return; }
    var view = P.files.view;
    GUI.get('api/pogos/projects').then(function (data) {
        P.files.projects = data;
        if (view === 'browse') {
            // the open project may have been deleted
            if (P.files.project && !data.projects.some(function (p) {
                return p.name === P.files.project.name; })) {
                P.files.openView('projects');
                return;
            }
            P.files.list(P.files.dir || P.files.root);
        } else if (view === 'projects') {
            P.files.renderProjects();
        } else if (view === 'home') {
            P.files.renderHome();
        }
    }).catch(GUI.fail);
    // the download list (home card counts / downloads page)
    if (view === 'home' || view === 'downloads') {
        P.files.loadDownloads();
    }
};

P.files.showView = function (view, title) {
    // show one page of the project manager (home / projects / downloads /
    //   browse)
    P.files.view = view;
    var home = view === 'home';
    P.$('pm-home').style.display = home ? '' : 'none';
    P.$('pm-bar').style.display = home ? 'none' : '';
    P.$('pm-projects').style.display = view === 'projects' ? '' : 'none';
    P.$('pm-downloads').style.display = view === 'downloads' ? '' : 'none';
    P.$('pm-browser').style.display = view === 'browse' ? '' : 'none';
    var filtered = view === 'projects' || view === 'downloads';
    P.$('pm-filter').style.display = filtered ? '' : 'none';
    P.$('pm-count').style.display = filtered ? '' : 'none';
    P.$('pm-filter').placeholder = view === 'downloads' ?
        'Filter downloads by file, type, project or parameter' :
        'Filter projects by name';
    if (title) { P.$('pm-title').textContent = title; }
    // the back button goes up one level
    P.$('pm-back').innerHTML = view === 'browse' && P.files.project ?
        '&larr; All projects' : '&larr; Project manager';
};

P.files.home = function () {
    // back to the four cards
    P.files.root = null;
    P.files.project = null;
    P.files.dir = null;
    P.files.showView('home');
    P.files.refresh();
};

P.files.back = function () {
    if (P.files.view === 'browse' && P.files.project) {
        P.files.openView('projects');
    } else {
        P.files.home();
    }
};

P.files.openView = function (view) {
    // open a page from the home cards
    var data = P.files.projects;
    P.$('pm-filter').value = '';
    if (view === 'projects') {
        P.files.root = null;
        P.files.project = null;
        P.files.showView('projects', 'Projects data');
        P.files.renderProjects();
    } else if (view === 'downloads') {
        P.files.showView('downloads', 'Downloaded data');
        P.files.loadDownloads();
    } else if (view === 'yamls' && data) {
        P.files.openRoot(data.yaml_dir, 'Yaml files');
    } else if (view === 'state' && data) {
        P.files.openRoot(data.state_dir, 'GUI files');
    }
};

P.files.renderHome = function () {
    // the counts shown on the home cards
    var data = P.files.projects;
    if (data) {
        P.$('pm-card-projects').textContent = data.projects.length +
            ' project(s)';
        P.$('pm-card-yamls').textContent = data.yamls.length +
            ' yaml file(s)';
        P.$('pm-card-state').textContent = data.state_dir;
    }
    var dl = P.files.downloads;
    P.$('pm-card-downloads').textContent = dl ? dl.nfiles + ' file(s) ' +
        '\u00b7 ' + GUI.fmtBytes(dl.size) + ' \u00b7 ' + dl.nlinks +
        ' link(s) in projects' : '...';
};

P.files.statsText = function (stats) {
    return stats ? stats.nfiles + ' files &middot; ' +
        GUI.fmtBytes(stats.size) : '...';
};

P.files.renderProjects = function () {
    // one row per project (sizes are counted in the background)
    var data = P.files.projects;
    var holder = P.$('pm-list');
    if (!data) { return; }
    if (data.projects.length === 0) {
        holder.innerHTML = '<div class="pm-empty muted">No projects yet - ' +
            'create one on the Setup tab.</div>';
        P.$('pm-count').textContent = '';
        return;
    }
    var filter = P.$('pm-filter').value.trim().toLowerCase();
    var shown = data.projects.filter(function (proj) {
        return !filter || proj.name.toLowerCase().indexOf(filter) >= 0;
    });
    P.$('pm-count').textContent = (filter ? shown.length + ' of ' : '') +
        data.projects.length + ' project(s)';
    if (shown.length === 0) {
        holder.innerHTML = '<div class="pm-empty muted">No project name ' +
            'matches "' + GUI.esc(filter) + '".</div>';
        return;
    }
    holder.innerHTML = shown.map(function (proj) {
        return '<div class="pm-row" data-name="' + GUI.esc(proj.name) +
            '"><span class="pm-name" title="' + GUI.esc(proj.path) + '">' +
            '&#128193; ' + GUI.esc(proj.name) + '</span><span ' +
            'class="pm-mods">' + (proj.modules.map(function (m) {
                return '<span class="pill">' + GUI.esc(m) + '</span>';
            }).join(' ') || '<span class="muted">none</span>') + '</span>' +
            '<span class="pm-yamls small">' + (proj.yamls.map(function (y) {
                return '<span class="mono">' + GUI.esc(GUI.basename(y)) +
                    '</span>';
            }).join('<br>') || '<span class="muted">none</span>') +
            '</span><span class="num small nowrap" data-stats="' +
            GUI.esc(proj.name) + '">' +
            P.files.statsText(P.files.stats[proj.name]) + '</span><span ' +
            'class="small nowrap muted">' + GUI.fmtTime(proj.mtime) +
            '</span><span class="row-actions nowrap"><button ' +
            'class="small" data-act="open">Open</button><button ' +
            'class="small danger" data-act="delete">Delete / reset...' +
            '</button></span></div>';
    }).join('');
    var byName = function (name) {
        return data.projects.filter(function (p) {
            return p.name === name; })[0];
    };
    holder.querySelectorAll('.pm-row').forEach(function (row) {
        var proj = byName(row.getAttribute('data-name'));
        row.onclick = function () { P.files.openProject(proj); };
        row.querySelector('[data-act="delete"]').onclick = function (ev) {
            ev.stopPropagation();
            P.files.deleteProject(proj);
        };
    });
    var todo = shown.filter(function (p) { return !P.files.stats[p.name]; });
    var next = function () {
        var proj = todo.shift();
        if (!proj) { return; }
        GUI.get('api/pogos/project_stats', {name: proj.name})
            .then(function (stats) {
                P.files.stats[proj.name] = stats;
                holder.querySelectorAll('[data-stats]').forEach(function (el) {
                    if (el.getAttribute('data-stats') === proj.name) {
                        el.innerHTML = P.files.statsText(stats);
                    }
                });
                next();
            }).catch(function () { next(); });
    };
    next();
};

P.files.openRoot = function (root, label, project) {
    // browse one project / data folder (never above it)
    P.files.root = root;
    P.files.rootLabel = label;
    P.files.project = project || null;
    P.files.showView('browse', label);
    P.files.list(root);
};

P.files.openProject = function (proj) {
    P.files.openRoot(proj.path, 'Project: ' + proj.name, proj);
};

P.files.list = function (dir) {
    return GUI.get('api/fs/list', {path: dir}).then(function (data) {
        P.files.dir = data.path;
        P.files.data = data;
        P.files.checked = {};
        P.$('files-all').checked = false;
        var root = P.files.root;
        P.$('files-up').disabled = !root || data.path === root;
        // bread crumbs relative to the project / data folder
        var rel = root && data.path.indexOf(root) === 0 ?
            data.path.substring(root.length) : data.path;
        var html = '<a data-p="' + GUI.esc(root) + '">' +
            GUI.esc(GUI.basename(root)) + '</a>';
        var acc = root;
        rel.split('/').filter(Boolean).forEach(function (part) {
            acc += '/' + part;
            html += ' / <a data-p="' + GUI.esc(acc) + '">' + GUI.esc(part) +
                '</a>';
        });
        var crumbEl = P.$('files-crumbs');
        crumbEl.innerHTML = html;
        crumbEl.querySelectorAll('a').forEach(function (a) {
            a.onclick = function () { P.files.list(a.getAttribute('data-p')); };
        });
        P.files.renderProjectHead();
        P.files.render();
    }).catch(GUI.fail);
};

P.files.up = function () {
    if (P.files.data && P.files.data.parent &&
        P.files.dir !== P.files.root) {
        P.files.list(P.files.data.parent);
    }
};

P.files.renderProjectHead = function () {
    var proj = P.files.project;
    var head = P.$('files-project-head');
    if (!proj) { head.innerHTML = ''; return; }
    var stats = P.files.stats[proj.name];
    head.innerHTML = '<div class="project-head"><b>' + GUI.esc(proj.name) +
        '</b><span class="muted small grow">' + proj.modules.length +
        ' module(s)' + (stats ? ' &middot; ' + stats.nfiles + ' files ' +
        '&middot; ' + GUI.fmtBytes(stats.size) : '') + ' &middot; used by ' +
        proj.yamls.length + ' yaml(s)' + (proj.yamls.length ? ': ' +
        proj.yamls.map(function (y) {
            return GUI.esc(GUI.basename(y)); }).join(', ') : '') +
        '</span><button class="small danger" id="files-del-project">Delete ' +
        '/ reset project...</button></div>';
    P.$('files-del-project').onclick = function () {
        P.files.deleteProject(proj);
    };
};

P.files.render = function () {
    var data = P.files.data;
    var body = P.$('files-body');
    if (!data) { body.innerHTML = ''; return; }
    var filter = P.$('files-filter').value.toLowerCase();
    var sort = P.files.sort;
    var entries = data.entries.filter(function (ent) {
        return !filter || ent.name.toLowerCase().indexOf(filter) >= 0;
    });
    entries.sort(function (a, b) {
        if ((a.kind === 'dir') !== (b.kind === 'dir')) {
            return a.kind === 'dir' ? -1 : 1;
        }
        var va = a[sort.key] || 0;
        var vb = b[sort.key] || 0;
        if (sort.key === 'name') { va = a.name.toLowerCase();
                                   vb = b.name.toLowerCase(); }
        var cmp = va < vb ? -1 : (va > vb ? 1 : 0);
        return sort.asc ? cmp : -cmp;
    });
    P.$('files-note').textContent = entries.length + ' item(s)' +
        (data.truncated ? ' (listing truncated)' : '') +
        (data.error ? ' - ' + data.error : '');
    if (entries.length === 0) {
        body.innerHTML = '<tr><td colspan="6" class="muted">Empty ' +
            'directory.</td></tr>';
        return;
    }
    body.innerHTML = entries.map(function (ent, index) {
        var actions = '';
        if (ent.kind === 'fits') {
            actions += '<button data-act="view">Header / data</button>';
        } else if (ent.kind !== 'dir') {
            actions += '<button data-act="view">View</button>';
        }
        if (/\.ya?ml$/.test(ent.name)) {
            actions += '<button data-act="edit">Edit</button>';
        }
        if (ent.kind !== 'dir') {
            actions += '<a href="' + GUI.rawUrl(ent.path, '&download=1') +
                '"><button>Download</button></a>';
        }
        actions += '<button class="danger" data-act="delete">Delete</button>';
        return '<tr data-index="' + index + '"><td><input type="checkbox">' +
            '</td><td class="fb-icon">' + GUI.FILE_ICONS[ent.kind] + '</td>' +
            '<td class="fb-name">' + GUI.esc(ent.name) + '</td><td ' +
            'class="num small">' + GUI.fmtBytes(ent.size) + '</td><td ' +
            'class="small nowrap muted">' + GUI.fmtTime(ent.mtime) + '</td>' +
            '<td class="row-actions">' + actions + '</td></tr>';
    }).join('');
    body.querySelectorAll('tr').forEach(function (tr) {
        var ent = entries[Number(tr.getAttribute('data-index'))];
        tr.querySelector('input').onchange = function () {
            P.files.checked[ent.path] = this.checked;
        };
        tr.querySelector('.fb-name').onclick = function () {
            if (ent.kind === 'dir') { P.files.list(ent.path); }
            else { GUI.viewFile(ent.path); }
        };
        tr.querySelectorAll('[data-act]').forEach(function (btn) {
            btn.onclick = function () {
                var act = btn.getAttribute('data-act');
                if (act === 'view') { GUI.viewFile(ent.path); }
                if (act === 'edit') { P.edit.open(ent.path); }
                if (act === 'delete') { P.files.remove([ent.path]); }
            };
        });
    });
};

P.files.selectAll = function (on) {
    document.querySelectorAll('#files-body input[type=checkbox]')
        .forEach(function (box) { box.checked = on;
                                  box.dispatchEvent(new Event('change')); });
};

P.files.selected = function () {
    return Object.keys(P.files.checked).filter(function (path) {
        return P.files.checked[path]; });
};

P.files.remove = function (paths) {
    if (paths.length === 0) { GUI.toast('Select files first'); return; }
    var list = paths.slice(0, 12).map(function (p) {
        return '<li><code>' + GUI.esc(p) + '</code></li>'; }).join('') +
        (paths.length > 12 ? '<li>... and ' + (paths.length - 12) +
         ' more</li>' : '');
    GUI.confirm('Delete ' + paths.length + ' item(s)', '<p>Permanently ' +
                'delete (directories with everything inside):</p><ul>' +
                list + '</ul>', 'Delete').then(function (ok) {
        if (!ok) { return; }
        GUI.post('api/fs/delete', {paths: paths}).then(function (res) {
            GUI.toast(res.message, res.success ? 'ok' : 'bad');
            P.files.stats = {};
            P.files.refresh();
        }).catch(GUI.fail);
    });
};

P.files.deleteSelected = function () { P.files.remove(P.files.selected()); };

P.files.diffSelected = function () {
    var paths = P.files.selected();
    if (paths.length !== 2) { GUI.toast('Select exactly 2 files', 'bad');
                              return; }
    GUI.showDiff({left: paths[0], right: paths[1], title: 'Compare files'});
};

P.files.deleteProject = function (proj) {
    // overlay: reset the project (pogos_reset - keeps inputs) or delete
    //   all of its data
    var stats = P.files.stats[proj.name];
    var yamls = proj.yamls;
    var canReset = yamls.length > 0;
    var body = '<p>What do you want to do with project <code>' +
        GUI.esc(proj.name) + '</code>' + (stats ? ' (' + stats.nfiles +
        ' files, ' + GUI.fmtBytes(stats.size) + ')' : '') + '?</p>' +
        '<div class="pm-del-choices">' +
        '<div class="pm-del-choice' + (canReset ? '' : ' disabled') + '">' +
        '<h4>&#8634; Just reset</h4><p>Runs <code>pogos_reset</code>: ' +
        'deletes (and recreates empty) the output / plot / temporary / ' +
        'other directories of the steps enabled in the yaml. Raw inputs ' +
        'and calibration files are kept, so the project can be run ' +
        'again.</p>' + (canReset ? (yamls.length > 1 ? '<label ' +
        'class="field-label" for="pm-reset-yaml">Yaml to reset with' +
        '</label><select id="pm-reset-yaml">' + yamls.map(function (y) {
            return '<option value="' + GUI.esc(y) + '">' +
                GUI.esc(GUI.basename(y)) + '</option>';
        }).join('') + '</select>' : '<p class="small muted">Uses <code>' +
        GUI.esc(GUI.basename(yamls[0])) + '</code>.</p>') +
        '<button id="pm-do-reset">Reset project...</button>' :
        '<p class="notice warn small">No yaml in <code>yamls/</code> uses ' +
        'this project, so POGOS cannot tell its inputs from its outputs - ' +
        'only deleting everything is possible.</p>') + '</div>' +
        '<div class="pm-del-choice danger"><h4>&#128465; Delete all ' +
        'data</h4><p>Permanently deletes <code>' + GUI.esc(proj.path) +
        '</code>: inputs, outputs and plots of every flavour.</p>' +
        (yamls.length ? '<label class="inline small"><input ' +
        'type="checkbox" id="pm-del-yamls"> Also delete the ' +
        yamls.length + ' yaml file(s) using it</label>' : '') +
        '<button class="danger" id="pm-do-delete">Delete all data...' +
        '</button></div></div>';
    GUI.dialog({id: 'pm-delete', title: 'Delete or reset ' + proj.name,
                body: body, buttons: [{label: 'Cancel'}]});
    var resetBtn = P.$('pm-do-reset');
    if (resetBtn) {
        resetBtn.onclick = function () {
            var choice = P.$('pm-reset-yaml');
            var yaml = choice ? choice.value : yamls[0];
            GUI.closeDialog('pm-delete');
            P.files.resetProject(yaml);
        };
    }
    P.$('pm-do-delete').onclick = function () {
        var box = P.$('pm-del-yamls');
        var alsoYamls = !!(box && box.checked);
        GUI.closeDialog('pm-delete');
        P.files.deleteAll(proj, alsoYamls);
    };
};

P.files.resetProject = function (yaml) {
    // reset through the Actions tab (preview, type RESET, console)
    P.selectYaml('act-select', yaml);
    P.act.selected();
    GUI.setTab('actions');
    P.act.reset();
};

P.files.deleteAll = function (proj, alsoYamls) {
    var stats = P.files.stats[proj.name];
    GUI.confirmTyped({
        title: 'Delete all data of ' + proj.name, word: proj.name,
        label: 'Delete project',
        html: '<p>Permanently delete <code>' + GUI.esc(proj.path) +
              '</code>' + (stats ? ' (' + stats.nfiles + ' files, ' +
              GUI.fmtBytes(stats.size) + ')' : '') + ' - inputs, outputs ' +
              'and plots of every flavour' + (alsoYamls ? ', and the ' +
              proj.yamls.length + ' yaml file(s) using it' : '') +
              '.</p><p class="muted">This cannot be undone.</p>'
    }).then(function (ok) {
        if (!ok) { return; }
        GUI.post('api/pogos/project_delete', {
            name: proj.name, confirm: proj.name, yamls: alsoYamls
        }).then(function (res) {
            GUI.toast(res.message, res.success ? 'ok' : 'bad');
            delete P.files.stats[proj.name];
            P.loadYamls();
            P.files.openView('projects');
            P.files.refresh();
        }).catch(GUI.fail);
    });
};

/* ---- Downloaded data (the shared download cache) ---- */
P.files.loadDownloads = function () {
    return GUI.get('api/pogos/downloads').then(function (data) {
        P.files.downloads = data;
        // forget ticked files that are gone
        var have = {};
        data.files.forEach(function (f) { have[f.path] = true; });
        Object.keys(P.files.dlChecked).forEach(function (path) {
            if (!have[path]) { delete P.files.dlChecked[path]; }
        });
        if (P.files.view === 'downloads') { P.files.renderDownloads(); }
        if (P.files.view === 'home') { P.files.renderHome(); }
    }).catch(GUI.fail);
};

P.files.dlLinkText = function (link) {
    // "project: KEY" (or the link path if it is outside the projects)
    return (link.project ? link.project : '(outside projects)') + ': ' +
        (link.key || 'unknown parameter');
};

P.files.dlShown = function () {
    // the downloads matching the filter, sorted
    var data = P.files.downloads;
    if (!data) { return []; }
    var filter = P.$('pm-filter').value.trim().toLowerCase();
    var shown = data.files.filter(function (f) {
        if (!filter) { return true; }
        var text = [f.rel, f.source, f.product || '', f.origin || '']
            .concat(f.links.map(P.files.dlLinkText)).join(' ').toLowerCase();
        return text.indexOf(filter) >= 0;
    });
    var sort = P.files.dlSort;
    shown.sort(function (a, b) {
        var va = a[sort.key], vb = b[sort.key];
        if (typeof va === 'string' || typeof vb === 'string') {
            va = String(va || '').toLowerCase();
            vb = String(vb || '').toLowerCase();
        } else { va = va || 0; vb = vb || 0; }
        var cmp = va < vb ? -1 : (va > vb ? 1 : 0);
        return sort.asc ? cmp : -cmp;
    });
    return shown;
};

P.files.renderDownloads = function () {
    var data = P.files.downloads;
    var body = P.$('dl-body');
    if (!data) { body.innerHTML = ''; return; }
    var shown = P.files.dlShown();
    P.$('pm-count').textContent = (shown.length !== data.files.length ?
        shown.length + ' of ' : '') + data.files.length + ' file(s) \u00b7 ' +
        GUI.fmtBytes(data.size);
    P.$('dl-note').innerHTML = 'Stored in <code>' + GUI.esc(data.path) +
        '</code>';
    P.$('dl-all').checked = false;
    if (data.files.length === 0) {
        body.innerHTML = '<tr><td colspan="8" class="muted">Nothing ' +
            'downloaded yet - online inputs (MAST / POGOS server) are ' +
            'stored here the first time a project needs them.</td></tr>';
        return;
    }
    if (shown.length === 0) {
        body.innerHTML = '<tr><td colspan="8" class="muted">No download ' +
            'matches the filter.</td></tr>';
        return;
    }
    body.innerHTML = shown.map(function (f, index) {
        var links = f.links.length ? f.links.map(function (link) {
            return '<div class="dl-link" title="' + GUI.esc(link.path) +
                '">' + (link.project ? '<span class="pill">' +
                GUI.esc(link.project) + '</span>' : '<span class="muted">' +
                '(outside projects)</span>') + ' <code>' +
                GUI.esc(link.key || 'unknown parameter') + '</code></div>';
        }).join('') : '<span class="muted">not used</span>';
        return '<tr data-index="' + index + '"><td><input type="checkbox"' +
            (P.files.dlChecked[f.path] ? ' checked' : '') + '></td>' +
            '<td class="dl-name" title="' + GUI.esc(f.path) + '"><span ' +
            'class="mono">' + GUI.esc(f.name) + '</span><div class="muted ' +
            'small">' + GUI.esc(f.origin || GUI.dirname(f.rel)) +
            '</div></td><td class="small nowrap">' +
            GUI.fmtTime(f.downloaded) + '</td><td><span class="pill dl-src-' +
            GUI.esc(f.source) + '">' + GUI.esc(f.source) + '</span></td>' +
            '<td class="mono small">' + GUI.esc(f.product || '-') + '</td>' +
            '<td class="num small nowrap">' + GUI.fmtBytes(f.size) + '</td>' +
            '<td class="dl-links small">' + links + '</td><td class="row-' +
            'actions nowrap"><button class="small" data-act="view">View' +
            '</button><button class="small danger" data-act="delete">' +
            'Delete...</button></td></tr>';
    }).join('');
    body.querySelectorAll('tr').forEach(function (tr) {
        var f = shown[Number(tr.getAttribute('data-index'))];
        tr.querySelector('input').onchange = function () {
            P.files.dlChecked[f.path] = this.checked;
        };
        tr.querySelector('[data-act="view"]').onclick = function () {
            GUI.viewFile(f.path);
        };
        tr.querySelector('[data-act="delete"]').onclick = function () {
            P.files.dlDelete([f]);
        };
    });
};

P.files.dlSelectAll = function (on) {
    P.files.dlShown().forEach(function (f) { P.files.dlChecked[f.path] = on; });
    document.querySelectorAll('#dl-body input[type=checkbox]')
        .forEach(function (box) { box.checked = on; });
};

P.files.dlDeleteSelected = function () {
    var data = P.files.downloads;
    var chosen = data ? data.files.filter(function (f) {
        return P.files.dlChecked[f.path]; }) : [];
    if (chosen.length === 0) { GUI.toast('Select downloaded files first');
                               return; }
    P.files.dlDelete(chosen);
};

P.files.dlLinksHtml = function (files, limit) {
    // the symlinks that break when these files are deleted (grouped by
    //   project)
    var links = [];
    files.forEach(function (f) { links = links.concat(f.links); });
    if (links.length === 0) {
        return {count: 0, html: '<p class="muted">No project links to ' +
                'these files - nothing breaks.</p>'};
    }
    var projects = {};
    links.forEach(function (link) {
        projects[link.project || '(outside projects)'] = true; });
    var names = Object.keys(projects).sort();
    var shown = links.slice(0, limit);
    var html = '<p class="notice warn small"><b>This breaks ' +
        names.length + ' project(s)</b> (' + names.map(GUI.esc).join(', ') +
        '): these ' + links.length + ' link(s) will point to missing files ' +
        'until the data are downloaded again (the next pogos_run of each ' +
        'project downloads them).</p><ul class="dl-break-list">' +
        shown.map(function (link) {
            return '<li><code>' + GUI.esc(link.path) + '</code><br><span ' +
                'class="muted small">' + GUI.esc(P.files.dlLinkText(link)) +
                '</span></li>';
        }).join('') + (links.length > shown.length ? '<li>... and ' +
        (links.length - shown.length) + ' more</li>' : '') + '</ul>';
    return {count: links.length, html: html};
};

P.files.dlDelete = function (files) {
    var size = files.reduce(function (sum, f) { return sum + f.size; }, 0);
    var list = files.slice(0, 8).map(function (f) {
        return '<li><code>' + GUI.esc(f.rel) + '</code></li>'; }).join('') +
        (files.length > 8 ? '<li>... and ' + (files.length - 8) +
         ' more</li>' : '');
    var broken = P.files.dlLinksHtml(files, 40);
    var html = '<p>Permanently delete ' + files.length + ' downloaded ' +
        'file(s) (' + GUI.fmtBytes(size) + '):</p><ul>' + list + '</ul>' +
        broken.html;
    var post = function () {
        GUI.post('api/pogos/downloads_delete', {
            files: files.map(function (f) { return f.path; }), confirm: true
        }).then(function (res) {
            GUI.toast(res.message, res.success ? 'ok' : 'bad');
            P.files.stats = {};
            P.files.loadDownloads();
        }).catch(GUI.fail);
    };
    var title = 'Delete ' + files.length + ' downloaded file(s)';
    if (broken.count === 0) {
        GUI.confirm(title, html, 'Delete').then(function (ok) {
            if (ok) { post(); } });
        return;
    }
    // breaking projects needs the word typed
    GUI.confirmTyped({title: title, word: 'DELETE', label: 'Delete',
                      html: html}).then(function (ok) {
        if (ok) { post(); } });
};

P.files.dlReset = function () {
    var data = P.files.downloads;
    if (!data || data.files.length === 0) {
        GUI.toast('Nothing downloaded');
        return;
    }
    var broken = P.files.dlLinksHtml(data.files, 60);
    GUI.confirmTyped({
        title: 'RESET: remove all downloaded data', word: 'RESET',
        label: 'Remove all downloaded data',
        html: '<p class="notice bad"><b>This deletes everything in</b> ' +
              '<code>' + GUI.esc(data.path) + '</code>: ' + data.nfiles +
              ' file(s), ' + GUI.fmtBytes(data.size) + '. Every project ' +
              'using downloaded data is broken until it is downloaded ' +
              'again.</p>' + broken.html +
              '<p class="muted">This cannot be undone.</p>'
    }).then(function (ok) {
        if (!ok) { return; }
        GUI.post('api/pogos/downloads_reset', {confirm: 'RESET'})
            .then(function (res) {
                GUI.toast(res.message, res.success ? 'ok' : 'bad');
                P.files.dlChecked = {};
                P.files.stats = {};
                P.files.loadDownloads();
            }).catch(GUI.fail);
    });
};

/* ==========================================================================
   Docs (full constant descriptions)
   ========================================================================== */
P.docs = {key: null, section: null, flavours: []};

P.docs.init = function () {
    P.$('docs-filter').oninput = P.debounce(P.docs.renderList, 150);
    P.$('docs-files-only').onchange = P.docs.renderList;
    P.$('docs-mode').onchange = function () {
        P.docs.mode = this.value;
        P.docs.key = null;
        P.docs.renderList();
    };
    GUI.onTab('docs', P.docs.renderList);
};

P.docs.group = function (key) {
    // the list group of a key: the first two parts (e.g. SOSSISSE.GENERAL)
    var parts = key.split('.');
    return parts.length > 2 ? parts.slice(0, 2).join('.') : parts[0];
};

P.docs.inPrefixes = function (key, prefixes) {
    return prefixes.some(function (pre) {
        return key === pre || key.indexOf(pre + '.') === 0; });
};

P.docs.flavourKeys = function (name) {
    // the keys of one flavour ('' = all, '_other' = keys of no flavour)
    var keys = Object.keys(P.params).sort();
    var flavours = P.docs.flavours;
    if (!name) { return keys; }
    if (name === '_other') {
        return keys.filter(function (key) {
            return !flavours.some(function (fl) {
                return P.docs.inPrefixes(key, fl.prefixes); });
        });
    }
    var fl = flavours.filter(function (f) { return f.name === name; })[0];
    return fl ? keys.filter(function (key) {
        return P.docs.inPrefixes(key, fl.prefixes); }) : keys;
};

P.docs.renderFlavours = function () {
    // the flavour dropdown (grouped by reduction level)
    var select = P.$('docs-flavour');
    var flavours = P.docs.flavours;
    var current = P.docs.constFlavour();
    var levels = [];
    flavours.forEach(function (fl) {
        if (levels.indexOf(fl.level) < 0) { levels.push(fl.level); }
    });
    var opt = function (value, label, count) {
        return '<option value="' + GUI.esc(value) + '"' + (value === current ?
            ' selected' : '') + '>' + GUI.esc(label) + ' (' + count +
            ')</option>';
    };
    var html = opt('', 'All flavours', Object.keys(P.params).length);
    levels.forEach(function (level) {
        var opts = flavours.filter(function (fl) {
            return fl.level === level; }).map(function (fl) {
                var n = P.docs.flavourKeys(fl.name).length;
                return n ? opt(fl.name, fl.name === 'GENERAL' ?
                               'General (GLOBAL / RUN)' : fl.name, n) : '';
            }).join('');
        if (opts) { html += '<optgroup label="' + GUI.esc(level) + '">' +
                    opts + '</optgroup>'; }
    });
    var other = P.docs.flavourKeys('_other').length;
    if (flavours.length && other) {
        html += '<optgroup label="Other">' + opt('_other', 'Shared / other',
                                                 other) + '</optgroup>';
    }
    select.innerHTML = html;
    if (select.value !== current) { select.value = ''; }
};

P.docs.matches = function () {
    // the keys shown in the list (flavour + search + file only), by group
    var filter = P.$('docs-filter').value.toLowerCase();
    var filesOnly = P.$('docs-files-only').checked;
    var groups = {};
    P.docs.flavourKeys(P.$('docs-flavour').value).forEach(function (key) {
        var info = P.params[key];
        if (filesOnly && !info.file) { return; }
        if (filter && (key + ' ' + info.description).toLowerCase()
            .indexOf(filter) < 0) { return; }
        (groups[P.docs.group(key)] = groups[P.docs.group(key)] || [])
            .push(key);
    });
    return groups;
};

P.docs.renderConstList = function () {
    var holder = P.$('docs-list');
    if (Object.keys(P.params).length === 0) {
        holder.innerHTML = '<p class="muted">Loading the constant ' +
            'descriptions...</p>';
        return;
    }
    P.docs.renderFlavours();
    var groups = P.docs.matches();
    var names = Object.keys(groups).sort();
    P.$('docs-count').textContent = names.reduce(function (n, g) {
        return n + groups[g].length; }, 0) + ' constant(s) in ' +
        names.length + ' section(s)';
    holder.innerHTML = names.map(function (group) {
        return '<div class="doc-group' + (group === P.docs.section &&
            !P.docs.key ? ' active' : '') + '" data-group="' +
            GUI.esc(group) + '" title="Show every constant of ' +
            GUI.esc(group) + '"><span>' + GUI.esc(group) + '</span><span ' +
            'class="doc-group-n">' + groups[group].length + '</span></div>' +
            groups[group].map(function (key) {
                var info = P.params[key];
                return '<div class="doc-item' + (key === P.docs.key ?
                    ' active' : '') + '" data-key="' + GUI.esc(key) + '">' +
                    GUI.esc(key.substring(group.length + 1) || key) +
                    (info.file ? ' <span class="pill">file</span>' : '') +
                    '</div>';
            }).join('');
    }).join('') || '<p class="muted">No constants match.</p>';
    holder.querySelectorAll('.doc-item').forEach(function (el) {
        el.onclick = function () { P.docs.render(el.getAttribute('data-key'));
                                   P.docs.markActive(); };
    });
    holder.querySelectorAll('.doc-group').forEach(function (el) {
        el.onclick = function () {
            P.docs.renderGroup(el.getAttribute('data-group'));
            P.docs.markActive();
        };
    });
};

P.docs.markActive = function () {
    document.querySelectorAll('#docs-list .doc-item').forEach(function (el) {
        el.classList.toggle('active', el.getAttribute('data-key') ===
                            P.docs.key);
    });
    document.querySelectorAll('#docs-list .doc-group').forEach(function (el) {
        el.classList.toggle('active', !P.docs.key &&
                            el.getAttribute('data-group') === P.docs.section);
    });
};

P.docs.constHtml = function (key, level) {
    // one constant: name, pills, type / default line, description
    var info = P.params[key];
    var tag = level === 3 ? 'h3' : 'h2';
    return '<' + tag + ' class="mono doc-key">' + GUI.esc(key) + '</' + tag +
        '><div class="yaml-summary"><span class="pill">' +
        GUI.esc(info.kind || '') + '</span>' + (info.file ?
        '<span class="pill run">file constant</span>' : '') +
        (info.user ? '<span class="pill ok">user setting</span>' : '') +
        '</div><div class="yf-meta" style="margin:8px 0">' +
        GUI.esc(P.paramMeta(info)) + '</div><pre class="doc-text">' +
        GUI.esc(info.description) + '</pre>';
};

P.docs.renderGroup = function (group) {
    // every constant of one section (e.g. EUREKA.GENERAL)
    P.docs.key = null;
    P.docs.section = group;
    var keys = P.docs.matches()[group] || Object.keys(P.params).filter(
        function (key) { return P.docs.group(key) === group; }).sort();
    var box = P.$('docs-detail');
    box.innerHTML = '<h2 class="mono">' + GUI.esc(group) + '</h2><div ' +
        'class="muted small">' + keys.length + ' constant(s) - click a ' +
        'name to show it on its own.</div>' + keys.map(function (key) {
            return '<div class="doc-entry" data-key="' + GUI.esc(key) + '">' +
                P.docs.constHtml(key, 3) + '</div>';
        }).join('');
    box.querySelectorAll('.doc-entry .doc-key').forEach(function (el) {
        el.onclick = function () {
            P.docs.render(el.parentNode.getAttribute('data-key'));
            P.docs.markActive();
        };
    });
    box.scrollTop = 0;
};

P.docs.render = function (key) {
    // the full description of one constant
    P.docs.key = key;
    P.docs.section = P.docs.group(key);
    var info = P.params[key];
    var box = P.$('docs-detail');
    if (!info) {
        box.innerHTML = '<p class="muted">Unknown constant ' + GUI.esc(key) +
            '</p>';
        return;
    }
    var inEdit = P.edit.outline && P.edit.outline.nodes.some(function (n) {
        return n.path.join('.') === key; });
    var group = P.docs.group(key);
    box.innerHTML = '<div class="doc-crumb"><a id="docs-to-group">' +
        GUI.esc(group) + '</a> &rsaquo;</div>' + P.docs.constHtml(key, 2) +
        (inEdit ? '<button class="primary" id="docs-to-edit">Show in Edit (' +
        GUI.esc(GUI.basename(P.edit.path)) + ')</button>' : '');
    P.$('docs-to-group').onclick = function () {
        P.docs.renderGroup(group);
        P.docs.markActive();
    };
    var btn = P.$('docs-to-edit');
    if (btn) {
        btn.onclick = function () {
            P.$('edit-filter').value = key;
            GUI.setTab('edit');
            P.edit.renderForm();
        };
    }
};

P.docs.popup = function (key) {
    // the full description of one constant in an overlay (the page under
    //   it stays where it was)
    if (!P.params[key]) {
        GUI.toast('No description for ' + key, 'bad');
        return;
    }
    GUI.dialog({id: 'docs-popup', title: 'Docs: ' + key,
                body: P.docs.constHtml(key, 2),
                buttons: [{label: 'Open in the Docs tab', onclick:
                           function (close) { close(); P.docs.show(key); }},
                          {label: 'Close', cls: 'primary'}]});
};

P.docs.show = function (key) {
    // open the Docs tab on one constant (in a flavour that shows it)
    GUI.setTab('docs');
    P.$('docs-filter').value = '';
    if (P.docs.menu !== 'constants') { P.docs.setMenu('constants'); }
    var flavour = P.docs.constFlavour();
    if (flavour && P.docs.flavourKeys(flavour).indexOf(key) < 0) {
        P.docs.stage = 'All';
    }
    P.docs.renderList();
    P.docs.render(key);
    P.docs.markActive();
    var el = document.querySelector('.doc-item[data-key="' +
                                    key.replace(/"/g, '\\"') + '"]');
    if (el) { el.scrollIntoView({block: 'center'}); }
};

/* ---- docs: menu (Algorithms / Constants), stage + flavour cards -------- */
// the stages of the cards (constants also have General / Other / All)
P.DOC_LEVELS = ['Pre-extraction', 'Extraction', 'Post-extraction'];

P.docs.setMenu = function (menu) {
    P.docs.menu = menu;
    GUI.store('docs-menu', menu);
    P.$('docs-menu-algorithms').classList.toggle('active',
                                                 menu === 'algorithms');
    P.$('docs-menu-constants').classList.toggle('active',
                                                menu === 'constants');
    P.$('docs-files-label').style.display = menu === 'constants' ? '' :
        'none';
    P.$('docs-detail').innerHTML = '<p class="muted">Choose an entry on ' +
        'the left.</p>';
    P.docs.key = null;
    P.docs.section = null;
    if (menu === 'algorithms') { P.docs.loadAlgorithms(); }
    P.docs.renderList();
};

P.docs.stages = function () {
    // the stage cards of the current menu
    if (P.docs.menu === 'algorithms') { return P.DOC_LEVELS.slice(); }
    return ['All', 'General'].concat(P.DOC_LEVELS).concat(['Other']);
};

P.docs.flavourList = function (stage) {
    // the flavour cards of a stage: [{name, count, disabled}]
    if (P.docs.menu === 'algorithms') {
        var data = P.docs.algo;
        if (!data) { return []; }
        return data.flavours.filter(function (fl) {
            return fl.level === stage; }).map(function (fl) {
                return {name: fl.name, disabled: !Object.keys(fl.plans)
                        .length};
            });
    }
    if (['All', 'General', 'Other'].indexOf(stage) >= 0) { return []; }
    return P.docs.flavours.filter(function (fl) {
        return fl.level === stage; }).map(function (fl) {
            var count = P.docs.flavourKeys(fl.name).length;
            return {name: fl.name, count: count, disabled: count === 0};
        });
};

P.docs.constFlavour = function () {
    // the constants filter value of the chosen stage / flavour
    var stage = P.docs.stage;
    if (stage === 'All') { return ''; }
    if (stage === 'General') { return 'GENERAL'; }
    if (stage === 'Other') { return '_other'; }
    return P.docs.flav || '';
};

P.docs.renderPick = function () {
    // the stage and flavour cards (and the instrument mode selector)
    var stages = P.docs.stages();
    if (stages.indexOf(P.docs.stage) < 0) { P.docs.stage = stages[0]; }
    var chip = function (value, label, active, disabled, extra) {
        return '<button class="chip' + (active ? ' active' : '') + '"' +
            (disabled ? ' disabled' : '') + ' data-chip="' +
            GUI.esc(value) + '">' + GUI.esc(label) + (extra ? ' <span ' +
            'class="chip-n">' + extra + '</span>' : '') + '</button>';
    };
    P.$('docs-stages').innerHTML = stages.map(function (stage) {
        return chip(stage, stage, stage === P.docs.stage, false, null);
    }).join('');
    var flavours = P.docs.flavourList(P.docs.stage);
    var usable = flavours.filter(function (fl) { return !fl.disabled; });
    if (!flavours.some(function (fl) {
        return fl.name === P.docs.flav && !fl.disabled; })) {
        P.docs.flav = usable.length ? usable[0].name : null;
    }
    P.$('docs-flavours').innerHTML = flavours.length ? flavours.map(
        function (fl) {
            return chip(fl.name, fl.name, fl.name === P.docs.flav,
                        fl.disabled, fl.disabled ? 'none' :
                        (fl.count === undefined ? null : fl.count));
        }).join('') : '<span class="muted small">' + (P.docs.menu ===
        'algorithms' && !P.docs.algo ? 'loading...' : (P.docs.stage ===
        'All' ? 'every constant' : P.docs.stage === 'Other' ?
        'constants shared by several flavours' : P.docs.stage ===
        'General' ? 'GLOBAL / RUN' : '-')) + '</span>';
    P.$('docs-stages').querySelectorAll('[data-chip]').forEach(function (b) {
        b.onclick = function () {
            P.docs.stage = b.getAttribute('data-chip');
            GUI.store('docs-stage', P.docs.stage);
            P.docs.key = null;
            P.docs.renderList();
        };
    });
    P.$('docs-flavours').querySelectorAll('[data-chip]').forEach(function (b) {
        b.onclick = function () {
            P.docs.flav = b.getAttribute('data-chip');
            GUI.store('docs-flav', P.docs.flav);
            P.docs.key = null;
            P.docs.renderList();
        };
    });
    // instrument modes (algorithms whose steps depend on the mode)
    var row = P.$('docs-mode-row');
    var plans = P.docs.menu === 'algorithms' ? P.docs.plansOf(P.docs.flav) :
        null;
    var modes = plans ? Object.keys(plans).filter(Boolean) : [];
    row.style.display = modes.length ? '' : 'none';
    if (modes.length) {
        if (modes.indexOf(P.docs.mode) < 0) { P.docs.mode = modes[0]; }
        P.$('docs-mode').innerHTML = modes.map(function (mode) {
            return '<option' + (mode === P.docs.mode ? ' selected' : '') +
                '>' + GUI.esc(mode) + '</option>';
        }).join('');
    }
};

P.docs.renderList = function () {
    if (!P.docs.menu) {
        P.docs.menu = GUI.recall('docs-menu', 'algorithms');
        P.docs.stage = GUI.recall('docs-stage', null);
        P.docs.flav = GUI.recall('docs-flav', null);
        P.docs.setMenu(P.docs.menu);
        return;
    }
    P.docs.renderPick();
    if (P.docs.menu === 'constants') {
        P.docs.renderFlavours();
        P.$('docs-flavour').value = P.docs.constFlavour();
        P.docs.renderConstList();
    } else {
        P.docs.renderAlgoList();
    }
};

/* ---- docs: algorithms ---------------------------------------------------- */
P.docs.loadAlgorithms = function () {
    if (P.docs.algo || P.docs.algoLoading) { return; }
    P.docs.algoLoading = true;
    P.$('docs-list').innerHTML = '<p class="muted">Reading the algorithm ' +
        'steps of every flavour (loads the reduction packages - a few ' +
        'seconds the first time)...</p>';
    GUI.get('api/pogos/algorithms').then(function (data) {
        P.docs.algoLoading = false;
        P.docs.algo = data;
        if (P.docs.menu === 'algorithms') { P.docs.renderList(); }
    }).catch(function (err) {
        P.docs.algoLoading = false;
        P.$('docs-list').innerHTML = '<div class="notice bad">' +
            GUI.esc(err.message) + '</div>';
    });
};

P.docs.plansOf = function (name) {
    var data = P.docs.algo;
    if (!data || !name) { return null; }
    var fl = data.flavours.filter(function (f) { return f.name === name; })[0];
    return fl ? fl.plans : null;
};

P.docs.currentPlan = function () {
    var plans = P.docs.plansOf(P.docs.flav);
    if (!plans) { return []; }
    return plans[P.docs.mode] || plans[''] || plans[Object.keys(plans)[0]] ||
        [];
};

P.docs.algoNode = function (index) {
    // a plan node from its index path ("0.2.1")
    var nodes = P.docs.currentPlan();
    var node = null;
    var names = [];
    index.split('.').forEach(function (part) {
        node = nodes[Number(part)];
        names.push(node.name);
        nodes = node.children;
    });
    return {node: node, names: names};
};

P.docs.renderAlgoList = function () {
    var holder = P.$('docs-list');
    if (!P.docs.algo) { P.docs.loadAlgorithms(); return; }
    var filter = P.$('docs-filter').value.toLowerCase();
    var count = 0;
    var rows = [];
    var walk = function (nodes, prefix, depth) {
        nodes.forEach(function (node, it) {
            var index = prefix ? prefix + '.' + it : String(it);
            var text = (node.name + ' ' + (node.func || '') + ' ' +
                        (node.desc || '')).toLowerCase();
            var start = rows.length;
            walk(node.children, index, depth + 1);
            var inner = rows.length > start;
            if (filter && text.indexOf(filter) < 0 && !inner) { return; }
            count++;
            rows.splice(start, 0, '<div class="algo-item' +
                (node.children.length ? ' algo-group' : '') +
                (index === P.docs.key ? ' active' : '') + '" data-algo="' +
                index + '" style="padding-left:' + (depth * 14 + 8) +
                'px">' + GUI.esc(node.name) + (node.loop ? ' <span ' +
                'class="pill">each item</span>' : '') + '</div>');
        });
    };
    walk(P.docs.currentPlan(), '', 0);
    P.$('docs-count').textContent = count + ' step(s)' + (P.docs.flav ?
        ' - ' + P.docs.flav : '');
    holder.innerHTML = rows.join('') || '<p class="muted">' + (P.docs.flav ?
        'No steps match.' : 'This stage has no flavour with steps.') +
        '</p>';
    holder.querySelectorAll('[data-algo]').forEach(function (el) {
        el.onclick = function () {
            P.docs.renderAlgo(el.getAttribute('data-algo'));
        };
    });
};

P.docs.codeCache = {};

P.docs.funcInfo = function (func) {
    // the source + docstring of a function (cached promise)
    if (!func) { return Promise.resolve(null); }
    if (!P.docs.codeCache[func]) {
        P.docs.codeCache[func] = GUI.get('api/code', {func: func});
    }
    return P.docs.codeCache[func];
};

P.docs.algoEntryHtml = function (node, index, level) {
    // one step: name, function, description (filled in later), code
    var tag = level === 3 ? 'h3' : 'h2';
    return '<' + tag + ' class="algo-name' + (level === 3 ? ' link' : '') +
        '" data-algo-go="' + index + '">' + GUI.esc(node.name) + '</' + tag +
        '><div class="yaml-summary">' + (node.loop ? '<span class="pill ' +
        'run">repeated for every item</span>' : '') + (node.children.length ?
        '<span class="pill">' + node.children.length + ' sub-step(s)' +
        '</span>' : '') + (node.desc ? '<span class="pill ok">' +
        'description</span>' : '') + '</div>' + (node.func ? '<div ' +
        'class="mono small algo-func">' + GUI.esc(node.func) + '</div>' : '') +
        '<pre class="doc-text" data-algo-desc="' + index + '">' +
        (node.desc ? GUI.esc(node.desc) : '<span class="muted">' +
         (node.func ? 'Loading the docstring...' : 'No description.') +
         '</span>') + '</pre>' + (node.func ? '<details class="algo-code" ' +
        'data-algo-code="' + index + '"><summary>Code</summary><div ' +
        'class="muted small">Loading...</div></details>' : '');
};

P.docs.renderAlgo = function (index) {
    // a step (and every sub-step of it) in the detail panel
    P.docs.key = index;
    var found = P.docs.algoNode(index);
    var node = found.node;
    var box = P.$('docs-detail');
    var html = '<div class="doc-crumb">' + GUI.esc(P.docs.flav) +
        (P.docs.mode ? ' (' + GUI.esc(P.docs.mode) + ')' : '') + ' &rsaquo; ' +
        found.names.slice(0, -1).map(GUI.esc).join(' &rsaquo; ') +
        '</div>' + P.docs.algoEntryHtml(node, index, 2);
    node.children.forEach(function (child, it) {
        html += '<div class="doc-entry">' + P.docs.algoEntryHtml(
            child, index + '.' + it, 3) + '</div>';
    });
    box.innerHTML = html;
    box.scrollTop = 0;
    // descriptions: XXXX_DESC, else the docstring of XXXX_FUNC
    box.querySelectorAll('[data-algo-desc]').forEach(function (pre) {
        var item = P.docs.algoNode(pre.getAttribute('data-algo-desc')).node;
        if (item.desc || !item.func) { return; }
        P.docs.funcInfo(item.func).then(function (info) {
            pre.innerHTML = info && info.doc ? GUI.esc(info.doc) +
                '<div class="muted small algo-src">(docstring of the ' +
                'function - no description written for this step)</div>' :
                '<span class="muted">' + GUI.esc(info && info.error ?
                info.error : 'No docstring.') + '</span>';
        }).catch(function () { return null; });
    });
    // the code loads when it is opened
    box.querySelectorAll('[data-algo-code]').forEach(function (det) {
        det.addEventListener('toggle', function () {
            if (!det.open || det.getAttribute('data-loaded')) { return; }
            det.setAttribute('data-loaded', '1');
            var item = P.docs.algoNode(det.getAttribute('data-algo-code'))
                .node;
            P.docs.funcInfo(item.func).then(function (info) {
                det.querySelector('div').outerHTML = '<div>' +
                    P.status.codeHtml(info, info.line) + '</div>';
                P.status.wireCopy(det);
            }).catch(GUI.fail);
        });
    });
    box.querySelectorAll('[data-algo-go]').forEach(function (el) {
        if (el.getAttribute('data-algo-go') === index) { return; }
        el.onclick = function () {
            P.docs.renderAlgo(el.getAttribute('data-algo-go'));
        };
    });
    document.querySelectorAll('#docs-list [data-algo]').forEach(function (el) {
        el.classList.toggle('active', el.getAttribute('data-algo') === index);
    });
};

/* ==========================================================================
   start up
   ========================================================================== */
document.addEventListener('DOMContentLoaded', function () {
    // consoles (one per page) and the processes table
    new GUI.Console('setup', 'console-setup', {title: 'Console (pogos_setup)',
                                                onDone: P.setup.done});
    new GUI.Console('edit', 'console-edit', {title: 'Console (pogos_edit)',
                                              onDone: function () {
                                                  P.loadYamls(); }});
    new GUI.Console('run', 'console-run', {title: 'Console (pogos_run)'});
    new GUI.Console('actions', 'console-actions',
                    {title: 'Console (pogos_config / pogos_reset)',
                     onDone: P.act.done});
    new GUI.Processes('processes', {tab: 'processes'});
    P.setup.init();
    P.edit.init();
    P.plots.init();
    P.files.init();
    P.docs.init();
    P.status.init();
    P.run.init();
    P.stream.init();
    P.$('batch-submit').onchange = P.run.previewBatch;
    GUI.onDataChange(function () { if (P.path) { P.loadYamls(); } });
    // the server state tells us the POGOS path (e.g. --path)
    GUI.onState = function (state) {
        if (state.path && state.path !== P.path) {
            P.pathOpened(state.path, null);
        } else if (!state.path && P.path) {
            // the worker restarted without a path
            P.path = null;
            P.setLocked(true);
        }
    };
    P.$('pogos-path').value = POGOS_INITIAL_PATH || GUI.recall('path', '');
    P.$('pogos-path').onkeydown = function (ev) {
        if (ev.key === 'Enter') { P.applyPath(); }
    };
    P.setLocked(!POGOS_INITIAL_PATH);
    if (POGOS_INITIAL_PATH) { P.pathOpened(POGOS_INITIAL_PATH, null); }
    else { P.autoOpenPath(GUI.recall('path', '')); }
    P.$('setup-data-path').value = POGOS_INITIAL_PATH || '';
    GUI.onTab('setup', function () {
        if (!P.$('setup-data-path').value) { P.setup.useGlobalPath(); }
    });
    P.loadParams();
    // deep links: #edit:/path/to.yaml or #run:/path/to.yaml
    var link = /^#(edit|run|actions):(.+)$/.exec(location.hash);
    if (link) { history.replaceState(null, '', '#' + link[1]); }
    GUI.init('info');
    if (link && P.path) {
        var target = decodeURIComponent(link[2]);
        P.loadYamls().then(function () {
            if (link[1] === 'edit') { P.edit.open(target); }
            else {
                var id = link[1] === 'run' ? 'run-select' : 'act-select';
                P.selectYaml(id, target);
                P[link[1] === 'run' ? 'run' : 'act'].selected();
            }
        });
    }
});
