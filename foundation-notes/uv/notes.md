# uv: Python Packaging and Project Management

`uv` is an extremely fast Python package and project manager, written in Rust.

## Python Version Management

### List Python Versions
```bash
uv python list
```
Shows all available Python versions and those already downloaded on your system.

### Find a Specific Version
```bash
uv python find 3.15
```
Locates the installation path for a specific Python version.

---

## Running Scripts and Files

### Run a Single File
```bash
uv run name.py
```

### Run with Temporary Dependencies
If a script requires packages that aren't installed in your environment, you can run it with on-the-fly dependency installation:
```bash
uv run --with rich --with pydantic name.py
```
You can use multiple `--with` flags to include all necessary packages.

---

## Script Initialization

To avoid long commands when running a specific script, you can initialize it with metadata:

### Initialize a Script
```bash
uv init --script name.py --python 3.14
```
After this, you only need to run:
```bash
uv run name.py
```

### Add Dependencies to a Script
```bash
uv add --script name.py "pydantic"
```

---

## Project Management

### Initialize a New Project
```bash
uv init
```
This creates a `pyproject.toml` file to manage your project.

### Manage Dependencies
Add dependencies easily:
```bash
uv add rich pydantic
```

Specify a version:
```bash
uv add rich==2.3
```

Remove a dependency:
```bash
uv remove rich
```

### Syncing and Locking

- **Note on Versions:** If your current Python version doesn't support a package, `uv` will return an error.
- **Manual Edits:** You can manually add dependencies to `pyproject.toml`. `uv` will automatically sync them the next time you run a command.
- **`uv sync`:** Automatically installs or removes packages to match your `pyproject.toml`.
- **`uv lock`:** Creates or updates the `uv.lock` file. Note that `uv sync` performs a lock automatically.