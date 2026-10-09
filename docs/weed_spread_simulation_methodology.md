# Weed model, policies and interpretation

This guide describes the implemented model used by `notebooks/demonstration.ipynb` and the final report. Earlier design ideas, such as a probabilistic occurrence rule or a physical buffer belt, are not the rules used in these experiments.

## Spatial inputs and initialisation

`utils/data_loader.py` joins ABS 2021 Census population to postcode-level land area derived from Landgate locality polygons. The same postcode density is assigned to each locality in that postcode. Postcodes 6000-6199 define the operational Perth study region; they are not an exact official metropolitan boundary.

The population-density initialisation is

$$
W_i^0 = W_{\min} + (W_{\max}-W_{\min})e^{-kD_i}.
$$

Here, $D_i$ is population density in people per square kilometre. The final case uses $W_{\min}=0.05$, $W_{\max}=1$ and $k=0.000783$. Higher population density is assumed to imply greater suppression and a lower initial Weed Index. This is a modelling assumption, not a fit to observed infestation.

Rasterisation in EPSG:7850 with a 1 km target cell size gives a 203 by 124 grid with 6,933 valid cells. Cells outside the selected land area are `NaN`. The initial regional mean is approximately 0.860575. The Weed Index is a relative model quantity, not measured biomass or an occurrence probability.

## Update order

One step is an abstract update, not a calibrated week. The simulator applies **growth → propagation → removal**, using the updated state at each stage.

### Natural growth

The discrete logistic update is

$$
G_i^t = rW_i^t\left(1-\frac{W_i^t}{K}\right),\qquad
W_i^{t,\mathrm{growth}} = W_i^t + G_i^t.
$$

The implementation clips the updated index to $[0,K]$; the reported case uses $K=1$ and $r=0.01$.

### Spatial propagation

For up to eight valid neighbours, propagation uses only positive differences:

$$
D_i^t = \alpha\sum_{j\in N_8(i)}
\max\left(W_j^{t,\mathrm{growth}}-W_i^{t,\mathrm{growth}},0\right),
$$

$$
W_i^{t,\mathrm{prop}} = W_i^{t,\mathrm{growth}}+D_i^t.
$$

The reported case uses $\alpha=0.01$. Values are clipped to $[0,K]$. Grid edges do not wrap, and invalid neighbours do not contribute. Despite the API name `diffusion`, this is **not mass-conserving diffusion**: it increases lower-index cells without subtracting from the source cells. A signed neighbour-difference sum would be a different model.

### Removal and cost

For a removal grid $R_i^t$ supplied by a registered policy,

$$
W_i^{t+1}=W_i^{t,\mathrm{prop}}-R_i^t.
$$

A policy returns a non-negative removal array and a scalar step cost, without changing its input grid. In the reported experiments, cost is **200 model-cost units per unit of index removed**, not a calibrated currency amount. Cumulative cost is the sum of step costs. The budget wrapper scales the last treatment if it would exceed the remaining cap; after exhaustion, growth and propagation continue with zero removal.

## Policies for sample 2036

Policy settings below apply to the post-growth, post-propagation state $X_i=W_i^{t,\mathrm{prop}}$.

| Parameter | Value |
|---|---:|
| A removal fraction $a$ | 0.15 |
| B removal fraction $b$ | 0.65 |
| Maximum treated cells per call $m$ | 50 |
| Density boundary $h$ | 0.70 |
| B lower threshold $\ell$ | 0.45 |
| Common budget cap | 250,000 model-cost units |
| Main horizon | 100 steps |

**Policy A** selects cells with $X_i\ge h$, ranks them from highest index to lowest, treats at most $m$, and removes fraction $a$ of each selected index.

**Policy B** considers $\ell\le X_i<h$ and ranks positive-score candidates using

$$
S_i=\sum_{j\in N_8(i)}\max(X_i-X_j,0).
$$

It treats at most $m$ cells and removes fraction $b$ of each selected index. This is a spread-oriented ranking within an index band, not the construction of a physical buffer belt. Both policies use stable sorting and reassess eligibility at every call.

## Schedules and reversal criterion

Baseline has no removal. A only and B only use their policy each step. AB starts with A and switches every step, giving 50 calls of each policy over 100 steps. The notebook additionally examines BA, A50B50, B50A50 and balanced random permutations of 50 A and 50 B calls. A mixed schedule makes one policy call per step; it does not apply both policies simultaneously.

For strategy $s$, the final relative change is

$$
\Delta_s=\frac{\overline W_s(T)-\overline W(0)}{\overline W(0)}.
$$

A Parrondo-type reversal requires $\Delta_A>0$, $\Delta_B>0$, $\Delta_{AB}<0$. The margin is

$$
M_{AB}=\min(\Delta_A,\Delta_B,-\Delta_{AB}).
$$

Baseline provides context but is not part of the sign test. The test concerns the final state, not monotonic increase or decrease throughout the run. The margin is not a confidence interval.

## Results and limits

At 100 steps, Baseline changes by +11.342%, A by +4.196%, B by +1.421%, and AB by -0.206%. Sample 2036 is the Step 08 candidate with additional schedule-control evidence; it is not the largest AB-margin example in the 2,400-condition search.

None of A, B or AB exhausts the original cap. Actual spending is approximately 149,107, 199,967 and 228,213 units respectively, so equal caps do not equalise expenditure. The reversal cannot be explained by budget exhaustion in this original run, and it does not establish superior cost efficiency.

No immediate A-to-B handoff was recorded. The two block schedules lose, but random orders can also win: the saved first 100 seeds give 46 decreases and the 200-seed extension gives 105. Random B target ranking makes AB increase in the three saved interventions. The reversal disappears when propagation is disabled (the single policies then win), at the lower matched cap of approximately 124,279 units, and at the tested 156-step horizon with a proportional cap of 390,000 units. These observations constrain possible explanations without establishing a unique mechanism.

The saved search samples 2,400 combinations, not the full Cartesian product. Its exact tested settings are preserved in `results/strong_parrondo_equal_budget_search.csv`; the original sampling script and seed have not been recovered. The consolidated notebook provides a smaller live sensitivity search, and marginal search associations should not be interpreted as isolated causal importance.

## Further reading

- [Demonstration notebook](../notebooks/demonstration.ipynb): live code, explanation cells and shared report-figure exports.
- [Step 08 validation](../notebooks/experiments/step08_parrondo_strong_condition_validation.ipynb): the selected candidate and additional schedule controls.
- [Final report](../report/CITS4403_25292965_25182537.pdf): scientific interpretation, references and AI-use disclosure.
- [CA API guide](weed_celluar_automana.md): simulator methods and policy interface.
- [Data-loader guide](gdf_dataloader.md): input preprocessing and population-density fields.
