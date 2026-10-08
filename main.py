from src.geo_to_graph import gdf_to_graph
import geopandas as gpd
from pathlib import Path
from src.geo_visualize import plot_geodataframe, plot_networkx
import matplotlib.pyplot as plt


geo_localities_path = Path('./data') / 'Localities_LGATE_234_WA_GDA2020_Public_Geopackage' / 'Localities_LGATE_234_WA_GDA2020_Public.gpkg'

regions = gpd.read_file(geo_localities_path.absolute())

# print(regions.info())

perth_metro = regions[
    regions["postcode"].astype(int).between(6000,6199)
]

metro_graph = gdf_to_graph(gdf=perth_metro, idx='name')



fig, ax = plt.subplots()

plot_geodataframe(perth_metro, ax=ax)
plot_networkx(metro_graph, ax=ax)

plt.axis("equal")
plt.show()
