# local-classyfire

Local SQLite cache and command-line tools for ClassyFire classification.

## Installation

Use the Docker environment described in [`../../env/README.md`](../../env/README.md).
It builds the pinned msentity C++ library and installs its Python binding.
For a local installation, install that native library first, then run:

```bash
python -m pip install -e .
local-classyfire --help
```

Installing the Python binding alone does not supply the native library.
The pinned msentity source and the CMake workaround for system HDF5 are
specified in `../../env/README.md`.

## Dataset annotation

```bash
local-classyfire annotate msdataset \
    --input input.msds --output classified.msds \
    --db cache.sqlite --identifier-column SMILES \
    --identifier-type smiles --add-tag
```

Dataset output supports `.msds`, `.msp`, and `.mgf`. `.h5` and `.hdf5`
output paths produce `.msds` files. Use `--no-overwrite` to retain existing
classification columns. Legacy `.msds` file compatibility must be checked
with representative input files before bulk processing.

## Tests

```bash
python -m unittest discover -s tests -p 'Test*.py'
```
