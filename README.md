# CITS4403 Parrondo Weed Control

Computational modelling of weed spread and control in the Perth metropolitan
area. The project compares individual weed-removal policies with alternating
policy schedules to investigate Parrondo-like effects.

Repository: <https://github.com/RayYouDS/cits4403-parrondo-weed-control>

## Parrondo demonstration and report

- [Executed Japanese demo](notebooks/parrondo_demo.ipynb): a ten-minute route
  through Steps 01–10, representative simulations, mechanism checks and limitations.
- [English report source](notebooks/parrondo_report.tex): A4, 11pt, one-inch
  margins. Compilation/page count is not yet verified: the desktop compiler
  failed during sandbox setup. Confirm final layout and team attribution before
  submission. The older `notebooks/report.md` is an earlier draft with different
  model descriptions; use the new report for these experiments.
- [Demo figures](notebooks/figures/parrondo_demo/): exported from the executed NB.

From the repository root, install Python 3 dependencies and launch the notebook:

```powershell
python -m pip install -r requirements.txt
python -m jupyterlab notebooks/parrondo_demo.ipynb
```

Choose **Restart Kernel and Run All**. Alternatively, execute every code cell
in a fresh Python process and save rich outputs/figures without a Jupyter server:

```powershell
python scripts/execute_parrondo_demo.py
```

The demo reruns seven representative controls plus an instrumented AB run.
It reads the saved Step10 CSVs rather than repeating the larger robustness study.
Required local data paths are:

- `data/Localities_LGATE_234_WA_GDA2020_Public_Geopackage/Localities_LGATE_234_WA_GDA2020_Public.gpkg`
- `data/2021 Census GCP Postal Areas for WA/2021Census_G01_WA_POA.csv`

Obtain missing inputs from the sources below, retaining these names. The demo
was verified with Python 3.14.4 in the existing project environment.

The representative condition supports a finite-horizon reversal, not permanent
suppression or uniquely periodic success. The proposed direct A-to-B threshold
handoff was **not observed** (zero events). Equal budget ceilings are not equal
realised expenditure. See the notebook for the evidence and remaining hypotheses.

## Project Resources

- [Weed Simulation Cellular Automaton Class](./docs/weed_celluar_automana.md)
- [Data Loader Module](./docs/gdf_dataloader.md)
- [Weed Simulation Methodology](./docs/weed_spread_simulation_methodology.md)

## Example Outputs

- Perth Population Heatmap

<img src="./docs/figures/perth_population_heatmep.png" width="600">

- Simulated Weed Index Distribution Heatmap

<img src="./docs/figures/weed_index_distribution.png" width="600">

## Data Sources

|Dataset|Description|Source|
|--|--|--|
|||[WA Localities](https://catalogue.data.wa.gov.au/dataset/localities)|
|||[Google Digital Elevation Data](https://developers.google.com/earth-engine/datasets/catalog/AU_GA_AUSTRALIA_5M_DEM)|
|||[Census DataPacks](https://www.abs.gov.au/census/find-census-data/datapacks?utm_source=gemini&release=2021&product=GCP&geography=POA&header=S)|


