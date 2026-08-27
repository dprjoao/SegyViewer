# SEG-Y Viewer

A desktop application for inspecting and visualizing SEG-Y seismic data, built with Python and PyQt.

The project aims to provide a simple and interactive environment for exploring seismic traces, SEG-Y metadata, and trace headers without loading the entire dataset into memory.

## Features

Current features include:

- Open and inspect SEG-Y files
- Interactive seismic section visualization
- Textual header visualization
- Binary header inspection
- Trace header inspection
- Trace navigation
- Search and filter trace header fields
- Display SEG-Y trace header byte positions and values
- Lazy access to seismic traces and headers

## Trace Inspector

The Trace Inspector provides access to the header information associated with individual seismic traces.

Each SEG-Y trace header field is displayed with its corresponding byte position, reserved field name, and stored value.

Examples include:

- Trace sequence number
- CDP
- Offset
- Source and receiver coordinates
- Inline
- Crossline
- Sample interval
- Number of samples

This makes it possible to inspect the internal organization of a SEG-Y file before making assumptions about its geometry.

## SEG-Y Reading

SEG-Y access is handled using `segyio`.

Files are opened without requiring geometry interpretation:

```python
segyio.open(
    path,
    mode="r",
    strict=False,
    ignore_geometry=True,
)
```

This allows the application to inspect SEG-Y files before defining which trace header fields represent inline, crossline, X and Y coordinates.

Seismic traces and headers are accessed on demand rather than requiring the entire dataset to be loaded into memory.

## Textual Header

The original textual header is preserved as raw bytes:

```python
textual_header_raw
```

and formatted for visualization using:

```python
segyio.tools.wrap()
```

The formatted representation is stored separately as:

```python
textual_header_wrapped
```

## Project Structure

```text
segy_viewer/
│
├── main.py
│
├── app/
│   └── main_window.py
│
├── segy/
│   ├── dataset.py
│   └── reader.py
│
├── ui/
│   ├── file_inspector.py
│   ├── icons.py
│   ├── theme.py
│   └── trace_inspector.py
│
├── plotting/
│   └── seismic_view.py
│
├── processing/
│
└── tests/
```

The project separates SEG-Y I/O, data representation, visualization and user interface components so that seismic processing and QC tools can be added independently.

## Requirements

- Python 3.10+
- PyQt
- NumPy
- segyio
- PyQtGraph

## Installation

Clone the repository:

```bash
git clone https://github.com/dprjoao/SegyViewer.git
cd segy_viewer
```

Create a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running

Start the application with:

```bash
python main.py
```

A SEG-Y file can also be supplied directly:

```bash
python main.py path/to/file.sgy
```

## Project Goals

The long-term goal is to build a lightweight desktop environment for SEG-Y inspection and seismic quality control.

Planned tools include:

- Multi-header trace inspection
- SEG-Y geometry analysis
- Inline and crossline navigation
- Geometry visualization
- Seismic display controls
- Gain and filtering
- Seismic attribute visualization
- Phase quality control

## Status

This project is currently under active development.

The current version focuses on establishing the SEG-Y reading, visualization and header-inspection infrastructure that will support the QC tools developed in later stages.
