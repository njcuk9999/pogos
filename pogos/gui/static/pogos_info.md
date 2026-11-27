## POGOS GUI

The POGOS gui (`pogos_gui`) runs the normal POGOS recipes for you -
`pogos_setup`, `pogos_edit`, `pogos_run`, `pogos_config` and `pogos_reset`
- and shows their output in a console on each page. Questions a recipe
still asks (e.g. an object name) are answered in that console. Every page
shows the **CLI equivalent** of what it runs, so anything done here can be
repeated from a terminal.

Start by entering the **POGOS path** at the top (or start the gui with
`pogos_gui --path=/path/to/pogos-data`). It is the `GLOBAL.DATA_PATH` of
your setups and holds `yamls/` (configuration files), `projects/` (the
inputs, outputs and plots of every project) and `pogos_gui/` (gui logs,
batch scripts and yaml backups). Hover over any parameter (setup fields,
edit rows) to see its full description, type, default and options.

## Tabs

- **Setup**: create a new yaml and directory structure with `pogos_setup`.
  Choose the data path, project and yaml names, the instrument and mode,
  the reduction steps, a demo to start from and how the input data are
  downloaded.
- **Edit**: load any yaml (from `yamls/` or anywhere on disk with
  **Browse disk**). Edit it as a form (**Parameters**, grouped by module
  with each parameter's description) or as **Raw YAML**, then **Review
  changes** side by side and **Save** (a backup is kept). **+ Add
  parameters** lists every POGOS constant that is not in the yaml yet
  (with its default and description); click **+** to add one, then set
  its value in the form. The **✕** next to a constant removes it from
  the yaml (after a confirmation showing the default it falls back to).
  **New project from this yaml** runs `pogos_edit`
  to copy it into a new project.
- **Run**: run a yaml with `pogos_run` on this machine (**Single
  Process**) or write / submit a Slurm script (**Batch Script**) using a
  template made in **Create Batch Template** (resources and activation
  lines such as `conda activate pogos-env`).
- **Actions**: check a yaml with `pogos_config` (report only, or fix
  interactively - the changes are then shown side by side), compare a
  yaml with its backups or any two files, and reset a project's outputs
  with `pogos_reset` (preview the directories, then type `RESET`).
- **Processes**: everything started from the gui (local processes and
  Slurm jobs) - open their logs or stop them.
- **Status**: where every `pogos_run` is (from the gui, a batch job or a
  terminal): a list of runs, and for each run its stages (pre-extraction /
  extraction / post-extraction), flavours (e.g. SOSSISSE) and sub steps
  with their status and progress. Click a step to open the log at that
  step. A step's **Plots** button opens the figures shown during it (and
  the steps inside it): light grey while figures may still come, dark
  grey once the step ended without any.
- **Plots**: **Stream** shows the figures a run displays (runs started
  from the gui stream their figures here instead of opening plot windows);
  **On disk** shows the plot files of every project, organised by project,
  module and directory. Click a plot for a full size view and use the
  arrow keys to move between plots. Streamed figures are interactive
  with matplotlib's own toolbar (zoom, pan, home / back / forward, shared
  axes, the coordinates under the mouse and matplotlib's key shortcuts
  once you click the figure - e.g. g grid, l / k log scales). Figures
  bigger than `APEROCORE_PLOT_STREAM_MAX_MB` (default 50 MB, 0 = off)
  stay static images.
- **Project manager**: choose a project to browse its modules, inputs,
  outputs and plots (view FITS headers / images / tables, text files and
  images, compare two files, delete files or the whole project), or open
  **Other data** (yaml files, gui state).
- **Docs**: the full description of every constant. Click a parameter
  name on the Setup / Edit tabs to jump to its description.

## Notes

- The gui listens on `localhost` only. From another machine use an ssh
  tunnel, e.g. `ssh -N -L 8097:localhost:8097 user@host`, then open
  `http://localhost:8097`.
- Jobs keep running if the browser is closed (find them again on the
  **Processes** tab). **Restart server** replaces a hung gui worker
  without stopping running jobs.
- Yaml files from an older POGOS version are refused by `pogos_run` /
  `pogos_reset` unless **Accept a yaml from an older POGOS version** is
  ticked (sets `POGOS_ACCEPT_OLD_YAML=1`); `pogos_config` can update them.
