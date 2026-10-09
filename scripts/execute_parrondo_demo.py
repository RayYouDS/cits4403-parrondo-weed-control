"""Execute the demo in a fresh Python process without launching a Jupyter server.

Run from the repository root: python scripts/execute_parrondo_demo.py
The notebook can also be run normally using Jupyter's Restart and Run All.
"""
from pathlib import Path
import base64
import time

import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root = Path(__file__).resolve().parents[1]
path = root / "notebooks/parrondo_demo.ipynb"
notebook = nbformat.read(path, as_version=4)
shell = InteractiveShell.instance()
import matplotlib
matplotlib.use("module://matplotlib_inline.backend_inline")
from matplotlib_inline.backend_inline import configure_inline_support, flush_figures
configure_inline_support(shell, "module://matplotlib_inline.backend_inline")

started = time.perf_counter()
figure_dir = root / "notebooks/figures/parrondo_demo"
figure_dir.mkdir(parents=True, exist_ok=True)
figure_number = 0
count = 0
for index, cell in enumerate(notebook.cells):
    if cell.cell_type != "code":
        continue
    count += 1
    print(f"Executing code cell {count} (notebook cell {index + 1})", flush=True)
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=True)
        flush_figures()
    cell.execution_count = count
    cell.outputs = []
    for name in ("stdout", "stderr"):
        value = getattr(captured, name)
        if value:
            cell.outputs.append(nbformat.v4.new_output("stream", name=name, text=value))
    for output in captured.outputs:
        cell.outputs.append(nbformat.v4.new_output(
            "display_data", data=output.data, metadata=output.metadata))
        if "image/png" in output.data:
            figure_number += 1
            (figure_dir / f"figure_{figure_number:02d}.png").write_bytes(
                base64.b64decode(output.data["image/png"]))
    nbformat.write(notebook, path)
    result.raise_error()
nbformat.validate(notebook)
print(f"Passed {count} code cells in {time.perf_counter()-started:.1f}s; {figure_number} figures.")
