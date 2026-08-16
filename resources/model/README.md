# TwoConnectedTanks simulation artifacts (PLACEHOLDER)

This folder is the **drop-in location** for the compiled OpenModelica model.
It is intentionally left empty in the repository because the build artifacts
are generated locally on the developer's Windows machine.

## What to place here

After compiling the `TwoConnectedTanks` model in OMEdit on Windows 10/11, copy
the following into this folder so that the launcher's *Browse* button can point
at them (or so you can keep them in one self-contained directory):

- `TwoConnectedTanks.exe` — the compiled simulation executable
- `TwoConnectedTanks_init.xml` — runtime initialization file (required!)
- Any dependency DLLs from the OpenModelica runtime, e.g.
  `libgcc_s_seh-1.dll`, `libstdc++-6.dll`, `libwinpthread-1.dll`,
  `sundials_*.dll` (the exact set depends on the solver you chose)
- `TwoConnectedTanks.mo` — the original Modelica source (optional, for reference)

## Why these must stay together

The launcher runs the executable with `setWorkingDirectory()` set to the
executable's own folder. On Windows, the `.exe` resolves its sibling runtime
DLLs and `*_init.xml` through the process working directory, so **all of these
files must remain in the same folder**. Moving the `.exe` out on its own will
cause a launch failure.

## Manual sanity check (once the .exe exists)

From a command prompt inside this folder:

```bat
TwoConnectedTanks.exe -override startTime=0,stopTime=4
```

This should run a full 0→4 s simulation and write result files next to the
executable.
