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

## Identifier columns (all formats)

`annotate msp`, `annotate mgf`, and `annotate msdataset` (alias `msds`) accept
these same identifier arguments:

- `--identifier-type smiles|inchikey`: defaults to `inchikey`.
- `--identifier-column NAME`: defaults to `SMILES` when the type is `smiles`,
  otherwise `InChIKey`.
- `--identifier` remains an alias for `--identifier-type` for existing scripts.

For example, select a custom SMILES column in any format:

```bash
local-classyfire annotate msp --input input.msp --output classified.msp \
    --db cache.sqlite --identifier-type smiles --identifier-column SMILES1
local-classyfire annotate mgf --input input.mgf --output classified.mgf \
    --db cache.sqlite --identifier-type smiles --identifier-column SMILES1
local-classyfire annotate msds --input input.msds --output classified.msds \
    --db cache.sqlite --identifier-type smiles --identifier-column SMILES1
```

MSP/MGF column matching ignores case, spaces, underscores, and hyphens, as in
the existing default-column matching. MSDS column names require an exact match.
Only the selected column is used; there is no fallback to another column or
identifier type. Column names and identifier values in the input are preserved,
including case-sensitive SMILES values. Other format-specific arguments, such
as `--style` for MSP/MGF and `--no-overwrite` for MSDS, remain separate.
