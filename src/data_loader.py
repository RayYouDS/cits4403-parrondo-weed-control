import geopandas as gpd
import pandas as pd
from pathlib import Path

# ================ Data Path ==============================
def load_locality_data(base_path:Path|None=None):
    if base_path is None:
        base_path = Path('data')

    localities_path = (
        base_path /
        "Localities_LGATE_234_WA_GDA2020_Public_Geopackage" /
        "Localities_LGATE_234_WA_GDA2020_Public.gpkg"
    )

    census_path = (
        base_path /
        "2021 Census GCP Postal Areas for WA" /
        "2021Census_G01_WA_POA.csv"
    )

    localities = gpd.read_file(localities_path)
    census = pd.read_csv(census_path)

    # Data cleaning: postcode -> int
    localities["postcode"] = localities["postcode"].astype(int)

    census["postcode"] = (
        census["POA_CODE_2021"]
        .str.replace("POA", "", regex=False)
        .astype(int)
    )

    # Aggregate land area
    postcode_area = (
        localities
        .groupby("postcode", as_index=False)
        .agg(
            total_land_area=("land_area", "sum")
        )
    )

    # Join census population
    postcode_stats = postcode_area.merge(
        census[["postcode", "Tot_P_P"]],
        on="postcode",
        how="left"
    )

    # Population density
    postcode_stats["population_density"] = (
        postcode_stats["Tot_P_P"]
        / postcode_stats["total_land_area"]
    )

    postcode_stats["population_density_km2"] = (
        postcode_stats["population_density"] * 1_000_000
    )

    # Join back
    localities = localities.merge(
        postcode_stats[
            [
                "postcode",
                "total_land_area",
                "Tot_P_P",
                "population_density",
                "population_density_km2"
            ]
        ],
        on="postcode",
        how="left"
    )

    return localities


if __name__ == "__main__":
    BASE_PATH = Path('data')

    localities = load_locality_data(BASE_PATH)

    print(localities['population_density_km2'][0:5])

    metro = localities[
        localities["postcode"].astype(int).between(6000,6199)
    ]

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 10))

    metro.plot(
        ax=ax,
        column="population_density_km2",
        cmap="YlOrRd",
        legend=True,
        edgecolor="black",
        linewidth=0.3
    )

    ax.set_title("Population Density in Perth Metropolitan Area")
    ax.set_axis_off()

    plt.show()