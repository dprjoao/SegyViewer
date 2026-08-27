# SEG-Y Viewer

Desktop SEG-Y inspection and visualization application built with Python,
PySide6, segyio and PyQtGraph.

## Current interface

The main workspace is split into:

- `Seismic View`
- `Trace Inspector`

A permanent file inspector contains:

- file information
- textual header
- binary header

The Trace Inspector contains:

- trace navigation
- selectable SEG-Y trace headers
- dynamic all-traces table

Each selected trace header becomes a column in the data table. Rows correspond
to SEG-Y trace indices.

Header arrays are loaded on demand using `segyio.attributes(...)` and cached in
the dataset.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

You can also open a file directly:

```powershell
python main.py "C:\data\survey.sgy"
```


## Visual refresh

The interface now uses a compact dark technical theme inspired by classic
seismic interpretation tools:

- permanent left SEG-Y information panel
- compact textual and binary header sections
- dark title bar on Windows
- top-level `Seismic View` and `Trace Inspector` tabs
- compact trace controls and summary cards
- selectable trace header table
- selected-header data table
- CSV export and clipboard copy
