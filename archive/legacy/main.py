# Resolve the repository from this notebook's directory or the repository root.
from pathlib import Path
import os
import sys
_start = Path.cwd().resolve()
repo_root = next(p for p in (_start, *_start.parents) if (p / "src" / "weed_ca.py").is_file())
os.chdir(repo_root)
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from utils.geo_to_graph import gdf_to_graph
import geopandas as gpd
from pathlib import Path
from utils.geo_visualize import plot_geodataframe, plot_networkx
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
