# CITS4403 Parrondo Weed Control

A Python cellular automaton for weed growth, spatial propagation and treatment in a Perth study region. The demonstration and report use **sample 2036**, the condition validated in Step 08. They compare Baseline, A only, B only and alternating AB, with additional schedule and mechanism checks in the notebook.

Repository: <https://github.com/RayYouDS/cits4403-parrondo-weed-control>

## 1. Get the project

Install Python 3 and Git, then open a terminal. The saved experiments were run with **Python 3.14.4**; dependencies are listed in `requirements.txt` and are not pinned to exact versions.

```powershell
git clone https://github.com/RayYouDS/cits4403-parrondo-weed-control.git
cd cits4403-parrondo-weed-control
```

If you already have the repository, open a terminal in its root (the folder containing `requirements.txt`, `src/` and `notebooks/`). Repository access is required while it is private.

## 2. Create a virtual environment

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name cits4403-weed --display-name "Python (CITS4403 Weed)"
```

If `python` is not recognised but the Python launcher is available, use `py -3 -m venv .venv` for the first command. If PowerShell blocks activation, activation can be skipped: use the environment's Python directly for each subsequent command, for example:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name cits4403-weed --display-name "Python (CITS4403 Weed)"
.\.venv\Scripts\python.exe -m jupyterlab notebooks/demonstration.ipynb
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name cits4403-weed --display-name "Python (CITS4403 Weed)"
```

The kernel registration points Jupyter to this environment. If you move or recreate `.venv`, register the kernel again from the new environment.

## 3. Check the input files

The repository includes the two inputs used by the demonstration. Keep these paths and filenames unchanged:

```text
data/Localities_LGATE_234_WA_GDA2020_Public_Geopackage/Localities_LGATE_234_WA_GDA2020_Public.gpkg
data/2021 Census GCP Postal Areas for WA/2021Census_G01_WA_POA.csv
```

The demonstration also reads `results/strong_parrondo_equal_budget_search.csv`, the saved 2,400-condition search. This is already included; you do not need to rerun that search to run the demonstration. An internet connection is needed for dependency installation, but the main demonstration uses local data rather than downloading observations.

If an input is missing, obtain the corresponding dataset from [Landgate Localities (LGATE-234)](https://catalogue.data.wa.gov.au/dataset/localities) or the [ABS 2021 Census DataPacks](https://www.abs.gov.au/census/find-census-data/datapacks). For Census data, use the Western Australia General Community Profile, Postal Areas, table G01. Retain the dataset metadata and licence files supplied alongside the inputs.

## 4. Open and run the demonstration

With the virtual environment active, run this from the repository root:

```powershell
python -m jupyterlab notebooks/demonstration.ipynb
```

1. Open `notebooks/demonstration.ipynb` and select **Python (CITS4403 Weed)** as the kernel.
2. Choose **Restart Kernel and Run All Cells**. In VS Code, select the same kernel, restart it, and choose **Run All**.
3. Let the cells finish in order. Animations, the local sensitivity search and 100 random policy orders take longer than simple plots; runtime depends on the machine.
4. Check that there is no error traceback and that the final code cell, **5.2 Timing, resources and horizon**, displays both result tables. Save the notebook to retain its outputs.

The notebook locates the repository root automatically. Its experiment and plotting code is written directly in notebook cells; no additional `.py` script needs to be run. It imports the existing model and policy implementations from `src/` and data utilities from `utils/`.

### Notebook route

| Part | What it demonstrates |
|---|---|
| Original walkthrough | Load locality/population data, initialise the Weed Index, rasterise, use the simulator and animations, register a simple example policy |
| Section 1 | Baseline, A only, B only and AB at the report settings; trajectories, expenditure and final-state comparison |
| Section 2 | The sign criterion and margin; explicitly schematic examples |
| Section 3 | Saved parameter search, marginal associations and a small live growth/propagation search |
| Section 4 | BA, A50B50, B50A50 and 100 balanced random policy orders |
| Section 5 | Immediate handoff, random B target ranking, propagation, matched expenditure and longer horizon |
| Section 6 | Interpretation, limitations, sources and report connection |

The simple removal function in the original walkthrough is an interface example, **not** Policy A or B. Read the explanation cells before the code cells. For a 10-minute demonstration, focus on the simulator, the main four-strategy result, the reversal criterion and selected controls; keep the detailed sensitivity outputs available for questions.

### Expected main result

Sample 2036 uses 1 km cells, 100 abstract steps, growth and propagation rates of 0.01, and a common budget cap of 250,000 model-cost units. The initial mean index is approximately 0.860575.

| Strategy | Final mean | Change from initial mean | Actual model cost |
|---|---:|---:|---:|
| Baseline | 0.958180 | +11.342% | 0 |
| A only | 0.896682 | +4.196% | 149,107 |
| B only | 0.872800 | +1.421% | 199,967 |
| AB | 0.858799 | -0.206% | 228,213 |

A reversal requires A and B individually to finish above the initial mean, while AB finishes below it. Baseline is context, not part of this sign test. The AB margin is approximately **0.206 percentage points**. None of the treated strategies exhausts the original cap at 100 steps, and equal caps do not mean equal actual expenditure.

### Generated outputs

Running the notebook refreshes files in these directories:

- `report/sample2036/`: the shared report figures `schematic.png` (A1) and `four_strategies.png` (A2), plus summary, trajectory and cost CSVs.
- `results/demonstration/`: additional schedule, sensitivity and mechanism tables and figures, including the final-state bar chart.

The LaTeX source uses the shared PNG files directly. Running the notebook updates those images; it **does not rebuild the submitted PDF**. The existing PDF can be read without installing LaTeX. To rebuild it after changing the figures or text, compile `report/report_en.tex` with pdfLaTeX twice from the repository root or the `report/` directory.

### Common execution issues

- **Missing module:** check that the selected notebook kernel is the registered virtual environment, then install `requirements.txt` using that environment's Python and restart the kernel.
- **Missing data file:** restore the input paths listed above. Changing the terminal directory is not a substitute for missing inputs.
- **Animation not visible in a saved notebook:** trust the notebook only if it is your own or from a trusted source, then rerun its animation cell. The animations embed HTML/JavaScript and require a supporting notebook viewer.
- **Stale or mixed results:** restart the kernel and run from the beginning after changing parameters. Do not combine results from different candidates or partially rerun only the plotting cells.

## Report and repository structure

The submitted report is [CITS4403_25292965_25182537.pdf](report/CITS4403_25292965_25182537.pdf): five pages of main text and eleven pages including references and appendices. Its editable source is [report_en.tex](report/report_en.tex). `report/report.md` is Ray's earlier draft, not the final report. The report includes an AI-use statement in Appendix C.

```text
src/                         Cellular automaton, treatment policies, experiment/schedule helpers
utils/                       Data loading, spatial conversion and visualisation
notebooks/demonstration.ipynb Main demonstration and report-figure generation
notebooks/experiments/        Steps 01-14 with detailed experiments and saved outputs
notebooks/validation/         Model and API checks
notebooks/exploratory/        Separate exploration of public weed observations
data/                        Input datasets, metadata and licences
results/                     Saved parameter searches and validation CSVs
results/demonstration/        Outputs generated by the consolidated demonstration
report/                      Submitted PDF, LaTeX source and original report draft
report/sample2036/           Shared report figures and main result tables
docs/                        Data-loader, simulator and model-rule documentation
archive/                     Historical notebooks and legacy material
requirements.txt             Python dependencies
```

## Further experiments and documentation

The detailed notebooks progress from baseline and individual policies (Steps 01-03) through alternation and search (Steps 04-09), robustness (Step 10), immediate handoff (Step 11), propagation (Step 12), B ranking (Step 13) and matched expenditure (Step 14). Inspect their run switches before starting expensive searches. Some earlier notebooks use other candidates; the final report and consolidated demonstration use **2036**.

- [Data loader](docs/gdf_dataloader.md)
- [Cellular automaton API](docs/weed_celluar_automana.md)
- [Model rules, policies and interpretation](docs/weed_spread_simulation_methodology.md)

The reversal is conditional on parameters, resources and endpoint. Block schedules lose in the selected example, but random policy orders can also succeed. No immediate A-to-B handoff was recorded. Randomising B's target ranking produces increases in the three saved checks, and the reversal disappears in the tested lower-cap and 156-step comparisons. These results do not identify a unique mechanism or predict observed weed abundance, weekly changes or monetary costs. Population-based initialisation is an uncalibrated modelling assumption. The exploratory observation-download notebook is separate and is not required to run the main demonstration.
