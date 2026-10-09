# CITS4403 Parrondo Weed Control

A spatial cellular automaton for weed spread and control in the Perth study area.
The project compares individual, alternating, block, and random policy schedules
to investigate conditional Parrondo-like reversals.

Repository: <https://github.com/RayYouDS/cits4403-parrondo-weed-control>

## Repository structure

```text
src/                        Model, policies, and experiment execution
utils/                      Data loading, spatial conversion, and visualisation
data/                       Input datasets, metadata, and licences
notebooks/
  demonstration.ipynb       Ray's demonstration; consolidation is pending
  experiments/              Steps 01-14, with saved outputs
  validation/               Model and API checks
  exploratory/              Public weed-data exploration
results/                    Saved experiment CSVs
  figures/                  Exported experiment figures
report/
  report.md                 Ray's report draft; final integration is pending
docs/                       Model documentation and explanatory figures
archive/                    Earlier demos, a separate report draft, and legacy entry points
```

## Setup and notebook execution

Use Python 3.x. The existing experiments were run with Python 3.14.4.
From the repository root:

```powershell
python -m pip install -r requirements.txt
python -m jupyterlab
```

Open a notebook and choose **Restart Kernel and Run All**. Notebooks locate the
repository root from their own directory or the repository root, so imports and
data paths also work in nested notebook folders. Long parameter searches and
robustness studies can be expensive; inspect their run switches first.
Saved CSVs and notebook outputs allow results to be reviewed without rerunning
the full search. There is no separate notebook execution script.

## Reading order

- [Demonstration](notebooks/demonstration.ipynb): Ray's existing demonstration.
  A single final presentation notebook will be prepared in the next phase.
- [Experiments](notebooks/experiments/): Steps 01-04 establish baseline and
  individual/mixed policies; Steps 05-09 search and validate parameters;
  Step10 checks duration, ecology, and random schedules.
- [Step11](notebooks/experiments/step11_handoff_validation.ipynb): immediate
  A-to-B handoff observations.
- [Step12](notebooks/experiments/step12_density_band_check.ipynb): normal versus
  disabled ecological spread.
- [Step13](notebooks/experiments/step13_ranking_feedback_check.ipynb): spatial
  feedback and B target-ranking intervention.
- [Step14](notebooks/experiments/step14_matched_expenditure_check.ipynb): verified
  matched expenditure and treatment timing.
- [Validation notebooks](notebooks/validation/): model and API checks.
- [Exploratory notebook](notebooks/exploratory/weed_data_eda.ipynb): public weed
  records, distinct from the population-based simulation initialisation.
- [Report draft](report/report.md): Ray's draft, awaiting integration with the
  latest experiments and final PDF preparation.

## Findings and scope

Candidate 2036 exhibits a 100-step reversal: individual policies increase the
mean Weed Index, whereas AB/BA reduce it. This is conditional on parameters,
time horizon, and treatment resources. A direct immediate A-to-B handoff was
not observed. Random policy orders can also succeed. The reversal disappears
at longer tested horizons and in the lower-budget matched-expenditure test.
B's spread-score targeting outperformed random target ranking in the tested
runs. These results do not establish a unique causal mechanism or predict
actual weed abundance or monetary costs.

## Data and outputs

Keep these input paths unchanged:

- `data/Localities_LGATE_234_WA_GDA2020_Public_Geopackage/Localities_LGATE_234_WA_GDA2020_Public.gpkg`
- `data/2021 Census GCP Postal Areas for WA/2021Census_G01_WA_POA.csv`

Dataset metadata and licences remain alongside the inputs. Obtain missing files
from the sources below and retain the stated filenames. Experiment CSVs are
written to `results/`. The exploratory notebook caches API responses in
`data/raw/`, writes tables to `data/processed/`, and exports figures to
`results/figures/weed_data_eda/`. Its API-derived data are not required for the
population-initialised experiments.

|Source|Use|
|---|---|
|[WA Localities](https://catalogue.data.wa.gov.au/dataset/localities)|Study-area polygons|
|[2021 Census DataPacks](https://www.abs.gov.au/census/find-census-data/datapacks)|Population inputs|
|[Google elevation dataset](https://developers.google.com/earth-engine/datasets/catalog/AU_GA_AUSTRALIA_5M_DEM)|Earlier exploration; not required by current experiments|

## Model documentation

- [Cellular automaton](docs/weed_celluar_automana.md)
- [Data loader](docs/gdf_dataloader.md)
- [Simulation methodology](docs/weed_spread_simulation_methodology.md)

## Finalisation status

Folder organisation is complete. Demonstration consolidation and report
integration remain to be done. Historical material is retained in
[archive](archive/); it is not the final report or presentation entry point.
