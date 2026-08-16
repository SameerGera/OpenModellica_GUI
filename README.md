# TwoConnectedTanks GUI Launcher

A small **PyQt6 desktop application** for launching a compiled OpenModelica
simulation. It provides an executable picker, start/stop
time inputs, a Run button, and a live console that streams the simulation
output. The launcher is the Python half of a FOSSEE / OpenModelica internship
screening task; the compiled `.exe` is produced separately by the user in
OMEdit on Windows (see below).



## Prerequisites

- Windows 10 / 11 (the compiled model and runtime DLLs are Windows-specific).
- Python 3.9 or newer.
- The compiled `TwoConnectedTanks.exe` together with its runtime DLLs and
  `TwoConnectedTanks_init.xml` (see *Building the executable*).

Install the Python dependencies:

```bat
python -m pip install -r requirements.txt
```

## Running the app

```bat
python main.py
```

1. Click **Browse** and select your `TwoConnectedTanks.exe`.
2. Set **Start time** (0–4) and **Stop time** (1–4).
3. Click **Run**. Console output streams live; the status line shows
   `Simulation completed` or `Simulation failed`.

## Building the executable (OMEdit)

1. Open OMEdit (part of [OpenModelica](https://openmodelica.org/)).
2. Load the `TwoConnectedTanks` model (the original `.mo` source, e.g. from the
   Modelica Standard Library or your own package).
3. Build / Simulate the model to produce `TwoConnectedTanks.exe`.
4. Copy `TwoConnectedTanks.exe`, `TwoConnectedTanks_init.xml`, and the required
   runtime DLLs into `resources/model/` (see `resources/model/README.md`).

Reference: [OpenModelica `-override` simulation flags](https://openmodelica.org/doc/OpenModelicaUsersGuide/latest/simulationflags.html#simflag-override).

## Constraint

The launcher enforces:

```
0 <= start time < stop time < 5
```

Start and Stop are integer seconds; the Run button is disabled and an inline
error is shown whenever this constraint is violated, so invalid launches are
prevented before the process starts.

## Important: keep the executable and its dependencies together

The launcher runs the executable with the process working directory set to the
executable's own folder. On Windows the `.exe` locates its sibling runtime
DLLs and `*_init.xml` through that directory, so **the `.exe`, the DLLs, and
the `_init.xml` must all stay in the same folder**. Moving the executable out
on its own will cause a launch failure.

## Manual sanity check

Once you have the `.exe`, from a command prompt inside its folder:

```bat
TwoConnectedTanks.exe -override startTime=0,stopTime=4
```

## Project layout

```
main.py                       # entry point
gui/main_window.py            # MainWindow (UI + signal wiring)
core/validators.py            # pure, Qt-free validation logic
core/simulation_runner.py     # SimulationRunner wrapping QProcess
resources/model/              # drop-in location for the .exe + DLLs
tests/test_validators.py      # unit tests for validation
```

## License

MIT — see [LICENSE](LICENSE).
