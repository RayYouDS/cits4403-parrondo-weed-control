# Originality and Contribution

Contributions:

- Ray You (25292965): CA Model Design
- Kaz Morita (Your student number): Cost Optimization

GitHub:

- https://github.com/RayYouDS/cits4403-parrondo-weed-control

# Background

Invasive species can cause substantial ecological and economic impacts by altering native ecosystems, reducing biodiversity, and increasing management costs. In urban and peri-urban environments, invasive weeds can spread across fragmented landscapes and may be influenced by both environmental conditions and human activity.

Weed management is particularly challenging because infestation is spatially heterogeneous. Some areas may have relatively high initial weed pressure, while neighbouring areas may remain at lower levels. Consequently, understanding how infestation changes both spatially and temporally is important for evaluating potential management strategies.

Conventional models that describe weed abundance primarily as a function of time may not adequately represent spatial propagation between neighbouring areas. A spatially explicit model is therefore useful for representing local interactions and the spread of infestation across a heterogeneous landscape.

Cellular Automata (CA) provide a relatively simple framework for representing such spatial dynamics by dividing a study area into discrete cells and updating the state of each cell according to its current state and those of its neighbouring cells.

# Research Aims

This study aims to develop a spatially explicit Cellular Automaton model to simulate the spread of weed infestation across the Perth metropolitan area. The model represents three main processes: natural growth of infestation, spatial propagation between neighbouring cells, and weed removal through management policies.

Specifically, the study investigates how weed infestation changes over time, how spatial propagation contributes to the expansion of high-infestation areas, and how management interventions affect both infestation levels and cumulative management costs.

# Model Specification

## Introduction

A Cellular Automaton (CA) was developed to simulate the spatiotemporal dynamics of weed infestation across the study area.

The study area was represented as a regular two-dimensional grid, with each cell representing a spatial unit of 500 m × 500 m. Each valid cell was assigned a Weed Index ranging from 0 to 1, representing the relative level of weed infestation. Cells outside the modelled land area were excluded from the simulation.

The state of each cell at timestep (t) is defined as:

$$
W_i^t \in [0,1]
$$

where $i$ denotes the cell, $t$ denotes the timestep, and $W_i^t$ represents the Weed Index of cell $i$ at timestep $t$.

The Weed Index is treated as a relative modelling quantity rather than a direct measurement of plant biomass or weed density. Therefore, changes in the Weed Index represent changes in the modelled level of infestation rather than direct changes in the physical quantity of weeds.

## Initialisation

The initial spatial distribution of weed infestation was modelled using an exponential decay function:

$$
W_i^0 =
W_{\min}+
(W_{\max}-W_{\min})
e^{-kD_i}
$$

where $D_i$ is the population density associated with cell $i$, $k$ is the pressure coefficient, and $W_{\min}$ and $W_{\max}$ define the minimum and maximum initial Weed Index, respectively.

Population data were obtained from the Australian Bureau of Statistics (ABS, 2021). Population density was calculated as the population divided by the corresponding land area and was used as a proxy for anthropogenic pressure.

Under this modelling assumption, higher population density results in a lower initial Weed Index, reflecting the hypothesis that areas experiencing greater human activity are subject to stronger weed suppression or management. Conversely, areas with lower population density are assumed to experience weaker anthropogenic suppression and therefore a higher initial Weed Index.

The pressure coefficient $k$ controls the sensitivity of the initial Weed Index to population density. A larger value of $k$ produces a more rapid decrease in the initial Weed Index as population density increases.


## Natural Growth

Natural growth was represented using a discrete-time logistic growth model. When the Weed Index is relatively low, the growth increment is approximately proportional to the current Weed Index. As the Weed Index approaches the carrying capacity, the growth rate decreases, representing a saturation effect.

The growth increment for cell $i$ at timestep $t$ is defined as:

$$
G_i^t =
rW_i^t
\left(
1-\frac{W_i^t}{K}
\right)
$$

The Weed Index is then updated according to:

$$
W_i^{t+1}=W_i^t+G_i^t
$$

where $r$ controls the growth rate and $K$ represents the maximum Weed Index supported by the model. Since the Weed Index is a relative modelling quantity, $K$ represents a model-defined upper bound rather than a directly measured ecological carrying capacity.

One simulation timestep represents one week. Therefore, $r$ is interpreted as a weekly model parameter controlling the rate of change in the Weed Index.

## Spatial diffusion

Spatial propagation was modelled using an eight-neighbour interaction structure. For each cell, the Weed Index was propagated only from neighbouring cells with a higher Weed Index to cells with a lower Weed Index. This directional rule represents the assumption that areas with greater infestation levels can contribute to the spread of infestation into surrounding areas.

Let $N_8(i)$ denote the set of up to eight neighbouring cells surrounding cell $i$. The propagation increment is defined as:

$$
D_i^t =
\alpha
\sum_{j\in N_8(i)}
\max(W_j^t-W_i^t,0)
$$

where $\alpha$ controls the strength of spatial propagation. The $\max(\cdot,0)$ function ensures that only neighbours with a higher Weed Index contribute to the propagation into cell $i$.

Following the propagation step, the Weed Index is updated as:

$$
W_i^{t,\mathrm{prop}}
=
W_i^{t,\mathrm{growth}}
+
D_i^t
$$

where $W_i^{t,\mathrm{growth}}$ denotes the Weed Index after the natural growth step and $W_i^{t,\mathrm{prop}}$ denotes the resulting state after spatial propagation.

This formulation represents directional spatial propagation rather than classical mass-conserving diffusion. The propagation term increases the Weed Index of lower-index cells without explicitly reducing the Weed Index of neighbouring source cells.

## Management and Removal

At each timestep, the model sequentially applies natural growth, spatial propagation, and management removal. The removal process is defined through a user-specified policy function, allowing different management strategies to be evaluated without modifying the underlying Cellular Automaton structure.

The sequence of computation is:

$$
W^t
\xrightarrow{\text{growth}}
W^{t,\mathrm{growth}}
\xrightarrow{\text{propagation}}
W^{t,\mathrm{prop}}
\xrightarrow{\text{removal}}
W^{t+1}
$$

The management policy determines the amount of Weed Index removed from each valid cell. Let $R_i^t$ denote the removal applied to cell $i$ during timestep $t$. The final state after management is therefore:

$$
W_i^{t+1}
=
W_i^{t,\mathrm{prop}}
-
R_i^t
$$

Management cost is calculated for each timestep as:

$$
C_t = \sum_i c_i^t
$$

where (c_i^t) represents the management cost associated with cell (i) at timestep (t). The cumulative management cost over the simulation is:

$$
\sum_{t=1}^{T} C_t
$$

This policy-based structure separates management decisions from the underlying CA dynamics, allowing alternative removal strategies and cost structures to be evaluated within the same spatial model.



# Experimental Design

Write your cost experiment here

# Results

Write your search result here

# Conclusions

Write your conclusions here

# References

1. Australian Bureau of Statistics (2021) Population: Census. Available at: https://www.abs.gov.au/statistics/people/population/population-census/latest-release (Accessed: 7 October 2026).


