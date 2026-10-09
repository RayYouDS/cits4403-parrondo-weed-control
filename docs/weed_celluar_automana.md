# Introduction

The Cellular Automaton (CA) related code has been encapsulated into the WeedCA class. While direct instantiation is supported, the recommended approach is to use the factory method `polygon_to_weedca()`:

```python
from src.weed_ca import WeedCA
from utils.data_loader import load_locality_data

localities = load_locality_data()
metro = localities[localities["postcode"].astype(int).between(6000, 6199)].copy()
weedca = WeedCA.polygon_to_weedca(metro,
                                  pressure_coef=0.000783,
                                  cell_size=1000,
                                  growth_rate=0.01,
                                  diffusion_rate=0.01)
```

# Object Properties

`WeedCA` objects have the following properties:

| Category | Attribute | Type | Description |
|---|---|---|---|
| Spatial Data | `gdf` | `GeoDataFrame` | A copy of the original polygon-based spatial dataset used to initialize and reset the simulation. |
| Spatial Data | `weed_grid` | `np.ndarray` (`float32`) | A 2D raster grid containing the current Weed Index of each simulation cell. Values are typically between 0 and the carrying capacity; invalid cells are represented by `NaN`. |
| Spatial Data | `valid_mask` | `np.ndarray` (`bool`) | A Boolean mask indicating which grid cells are valid for simulation. `True` represents valid cells, while `False` represents cells outside the simulation area. |
| Spatial Data | `transform` | `Affine` | The spatial transformation that maps grid row/column coordinates to geographic coordinates. It is used for geospatial referencing and exporting the simulation results. |
| Spatial Data | `crs` | `str` / CRS | The Coordinate Reference System (CRS) used by the spatial data and simulation grid. |
| Spatial Data | `cell_size` | `float` | The spatial size of each grid cell, typically measured in metres when using a projected CRS. |
| Initialization Parameters | `pressure_coef` | `float` | Coefficient controlling the effect of population density on the initial Weed Index. |
| Initialization Parameters | `w_min` | `float` | Minimum Weed Index used in the initialization function. |
| Initialization Parameters | `w_max` | `float` | Maximum Weed Index used in the initialization function. |
| Model Parameters | `growth_rate` | `float` | Rate controlling growth per abstract simulation step of the Weed Index under the logistic growth model. |
| Model Parameters | `carrying_capacity` | `float` | Maximum Weed Index that the logistic growth process approaches or is constrained by. |
| Model Parameters | `diffusion_rate` | `float` | Coefficient controlling the rate at which Weed Index spreads between neighbouring cells. |
| Policy | `policy` | `Callable` / `None` | The management policy applied during the removal phase. It receives the current Weed Index grid and valid-cell mask and returns the amount of weed removed and the associated cost. |
| Simulation State | `step_counter` | `int` | Number of simulation steps that have been completed. |
| Simulation State | `total_cost` | `float` | Cumulative cost of all management actions performed during the current simulation. |

# Examples

## How can I get the current weed status

Use `show_grid()` method to visualize current weed status:

```python
weedca.show_grid()
```

Example output:

<img src="figures/weed_show_fig.png" width="300">

## How can I push the CA to move forward

Simply call `step()` method to push the CA forward:

```python
weedca.step()
```

One step is an abstract model update. No conversion to weeks is calibrated in the final report or demonstration. Updates apply growth, propagation and removal in that order when all three modes are enabled.

## How can I get animated simulation

Call `animate()` method with the frame, FPS (frames per second) and modes (explained later) you want:

```python
weedca.animate(frames=100, fps=20, modes=['growth', 'diffusion'])
```

Example Output:

<img src="figures/anime_example.gif" width="300">

## How can I select the simulation methods I want

By passing a modes list to the simulation methods, the CA will only execute the specified processes:

```python
modes = ['growth', 'diffusion']
weedca.animate(frames=100, fps=20, modes=modes)
```

In this example, the removal process will be omitted from the simulation.

## How does the removal function work and how can I register my policy function to CA

First, define a policy function and register it using the `register_policy()` method:

```python
import numpy as np

def simple_removal(weed_grid, mask):
    # Return removal without modifying the simulator input.
    values = np.where(mask, weed_grid, 0)
    diff = values * 0.001
    cost = float(np.sum(diff) * 200)  # Model-cost units, not dollars.

    return diff, cost

weedca.register_policy(simple_removal)
```

The registered removal policy will then be applied during subsequent simulations when the removal mode is enabled.

The policy function receives the following parameters at each simulation step:

|Parameter|Meaning|
|---|---|
|weed_grid|A grid represent weed index at current timestep|
|valid_mask|A bool mask indicates valid cells (True -> Land; False -> Sea or out-of-boundary)|

The policy function should calculate the amount of Weed Index to remove from each cell and return:

- diff: a non-negative matrix with the same shape as weed_grid;
- cost: a scalar (float) representing the management cost for the current timestep.

The CA subsequently subtracts diff from the current Weed Index grid and adds cost to `total_cost`.

## Repeated simulations and policy state

`simulate(steps=100, modes=[...])` resets the grid to its initial state, resets the simulator's cost and step counter, and returns `(history, cost_history)`. Both arrays include step zero, so their first dimension has length 101. `animate(frames=100, ...)` uses this simulation history and returns an HTML animation. `fps` controls playback speed, not ecological time.

`WeedCA.reset()` does not reset a stateful registered policy. For independent scheduled/budgeted runs, construct a fresh policy or explicitly call its `reset()` before simulating. The `run_experiment()` helper does this policy reset automatically. `show_grid()` and `animate()` retain a dollar sign in the original display interface; interpret those values as model-cost units.

## Report and demonstration settings

Sample 2036 uses `pressure_coef=0.000783`, `cell_size=1000`, `growth_rate=0.01`, `diffusion_rate=0.01`, `carrying_capacity=1`, initial bounds 0.05 and 1, and 100 abstract steps. These values are explicit experiment settings, not necessarily the API defaults or calibrated ecological rates. See [model rules and policies](weed_spread_simulation_methodology.md) for the policy settings and reversal definition.

The earlier embedded images in this API guide illustrate the interface and may use older parameters. Use the current demonstration notebook and `report/sample2036/` for the final case's outputs.
