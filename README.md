# TwoConnectedTanks GUI Launcher

A **PyQt6 desktop application** for launching a compiled OpenModelica
simulation (`TwoConnectedTanks.exe`).  It provides an executable picker,
start / stop time inputs, a Run button, and a live colour-coded console
that streams the simulation output in real time.

Built as the Python half of a **FOSSEE / OpenModelica** screening task.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  main.py                                                │
│    └── run_application()                                │
│         ├── QApplication                                │
│         └── MainWindow (gui/main_window.py)             │
│              ├── File picker  (QLineEdit + QFileDialog) │
│              ├── Start / Stop (QSpinBox)                 │
│              ├── Run button   (QPushButton)              │
│              ├── Console area (QTextEdit, colour-coded)  │
│              └── SimulationRunner (core/simulation_runner.py)
│                   ├── QProcess with custom PATH env     │
│                   ├── -startTime=N  -stopTime=N flags   │
│                   └── Exit-code interpretation          │
│                        ├── 0        → success           │
│                        ├── 0xC0000135 → missing DLL     │
│                        └── other    → model error       │
│                                                         │
│  core/validators.py                                     │
│    ├── validate_time_range (0 ≤ start < stop < 5)       │
│    └── validate_executable (.exe exists)                 │
└─────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- **Windows 10 / 11** (the compiled model and runtime DLLs are Windows-specific).
- **Python 3.9** or newer.
- The compiled `TwoConnectedTanks.exe` together with its runtime DLLs (see below).

Install the Python dependencies:

```bat
pip install -r requirements.txt
```

---

## Running the App

```bat
python main.py
```

1. Click **Browse…** and select `resources/model/TwoConnectedTanks.exe`.
2. Set **Start time** (0–3 s) and **Stop time** (1–4 s).
3. Click **Run Simulation**.
4. Console output streams live; the status bar shows the result.

---

## Input Validation

The launcher enforces:

```
0 ≤ start time < stop time < 5
```

Both values are integer seconds.  The Run button is disabled and an
inline error message is shown whenever this constraint is violated,
preventing invalid launches before the process starts.

---

## OpenModelica Executable — CLI Flags

The compiled model accepts dedicated flags for simulation timing:

```bat
TwoConnectedTanks.exe -startTime=0 -stopTime=4
```

> **Note:** The `-override` flag is for overriding *model parameters*
> (e.g. `tank1.A=2`), **not** simulation start/stop times.

---

## Runtime Dependency Packaging

The executable links against **20 OpenModelica runtime DLLs** (~82 MB).
These are shipped in `resources/model/runtime/` so the application works
**without** a global OpenModelica installation.

The launcher's `SimulationRunner` prepends the `runtime/` directory to
the child process's `PATH` before launching the executable.

### Regenerating the runtime folder

If you need to re-copy the DLLs (e.g. after upgrading OpenModelica):

```bat
python scripts/copy_runtime.py
```

Edit `OM_BIN` in the script if your installation path differs from the
default `C:\Program Files\OpenModelica1.27.0-64bit\bin`.

### Key DLLs

| DLL | Purpose |
|-----|---------|
| `libSimulationRuntimeC.dll` | Core OpenModelica simulation engine |
| `libopenblas.dll` | BLAS / LAPACK linear algebra |
| `libsundials_*.dll` | CVODE, IDAS, KINSOL ODE/DAE solvers |
| `libgfortran-5.dll` | Fortran runtime (solvers) |
| `libgcc_s_seh-1.dll` / `libstdc++-6.dll` | MinGW C/C++ runtime |
| `libomcgc-1.dll` | OpenModelica garbage collector |

---

## Git LFS (Large File Storage)

This repository uses [Git LFS](https://git-lfs.com/) to manage the large binary files in the `resources/` directory (including the `.exe` and the ~82 MB of OpenModelica runtime `.dll` files).

**Cloning the repository:**
If you have Git LFS installed on your system, a standard `git clone` will automatically pull down the actual DLLs.
If your cloned `resources/model/runtime/` folder only contains small text pointer files (e.g., files that are ~130 bytes), you need to initialize LFS and pull the binaries:
```bat
git lfs install
git lfs pull
```

---

## Known Model Behaviour

The supplied `TwoConnectedTanks` model contains an equation in `Tank2.mo`:

```modelica
T = V / (Q1);
```

where `Q1 = 0` for all `time ≤ 5`.  This causes a **division-by-zero
assertion** at initialisation for any simulation within the GUI's valid
time range (`stop < 5`):

```
LOG_ASSERT | division by zero at time 0, (a=10) / (b=0),
             where divisor b expression is: tank2.Q1
```

This is a **model-level issue**, not a packaging or launcher bug.  The
GUI faithfully displays this output in the console so the user can
diagnose the problem.

---

## Building the Executable (OMEdit)

1. Open **OMEdit** (part of [OpenModelica](https://openmodelica.org/)).
2. Load the `NonInteractingTanks` package (the `.mo` source files).
3. Build / Simulate `TwoConnectedTanks` to produce the `.exe`.
4. Copy `TwoConnectedTanks.exe`, `*_init.xml`, and the companion files
   into `resources/model/`.
5. Run `python scripts/copy_runtime.py` to populate `resources/model/runtime/`.

---

## Project Structure

```
OpenModellica_FOSSE/
├── main.py                         # Entry point
├── requirements.txt                # PyQt6>=6.4
├── README.md
├── LICENSE
│
├── core/                           # Business logic (Qt-dependent)
│   ├── __init__.py
│   ├── simulation_runner.py        # QProcess wrapper, PATH env, exit codes
│   └── validators.py               # Pure validation functions
│
├── gui/                            # Presentation layer
│   ├── __init__.py
│   └── main_window.py              # MainWindow (UI + signal wiring)
│
├── resources/
│   └── model/
│       ├── TwoConnectedTanks.exe   # Compiled model
│       ├── TwoConnectedTanks.bat   # Reference launcher (not used by app)
│       ├── TwoConnectedTanks_init.xml
│       ├── TwoConnectedTanks_info.json
│       ├── TwoConnectedTanks_*.bin/.json/.mat
│       └── runtime/                # ← Packaged OpenModelica DLLs (20 files)
│           ├── libSimulationRuntimeC.dll
│           ├── libopenblas.dll
│           └── ... (18 more)
│
├── scripts/
│   └── copy_runtime.py             # DLL packaging helper
│
└── tests/
    ├── __init__.py
    └── test_validators.py          # Unit tests for validation
```

---

## Running Tests

```bat
python -m pytest tests/ -v
```

Or with `unittest`:

```bat
python -m unittest discover -s tests -v
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| App shows "Missing runtime DLLs (0xC0000135)" | `runtime/` folder is missing or incomplete | Run `python scripts/copy_runtime.py` |
| "override variable name not found: startTime" | Wrong CLI flags | Ensure `simulation_runner.py` uses `-startTime=N`, not `-override` |
| "division by zero at time 0 … tank2.Q1" | Model bug: `T = V/Q1` when `Q1 = 0` | Known issue in the supplied model |
| "No executable path provided" | No file selected | Click Browse and select the `.exe` |
| Run button stays disabled | Invalid time range | Ensure `0 ≤ start < stop < 5` |

---

## License

MIT — see [LICENSE](LICENSE).
