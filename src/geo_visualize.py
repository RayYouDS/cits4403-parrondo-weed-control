'''
This is an all-in-one visualization module of the whole project.
'''

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import geopandas
import networkx as nx


def plot_geodataframe(gdf: geopandas.GeoDataFrame, ax:Axes|None = None) -> Axes:
    '''
    Visualize geopanda dataframe to matplotlib plot
    '''
    if not isinstance(gdf, geopandas.GeoDataFrame):
        raise ValueError('Input must be GeoDataFrame')

    if ax is None:
        fig, ax = plt.subplots()

    gdf.plot(ax=ax,
            facecolor="lightgray",
            edgecolor="black")

    return ax


def plot_networkx(G: nx.Graph, ax:Axes|None = None) -> Axes:
    '''
    Visualize networkX graph to nx built-in plot
    '''
    if not isinstance(G, nx.Graph):
        raise ValueError('Input must be networkX Graph')

    if ax is None:
        fig, ax = plt.subplots()

    pos = {
        node: (
            data["x"],
            data["y"]
        )
        for node, data in G.nodes(data=True)
    }

    nx.draw(G=G,
            pos=pos,
            ax=ax,
            node_color='C1',
            node_shape='s',
            node_size=5,
            with_labels=False,
            font_size=3)

    return ax
    

if __name__ == "__main__":
    # Test raise
    plot_networkx('a')