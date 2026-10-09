import geopandas as gpd
import networkx as nx



def gdf_to_graph(gdf: gpd.GeoDataFrame, idx:str) -> nx.Graph:
    """
    Convert a GeoDataFrame into an undirected NetworkX graph.

    Notes
    -----
    - Only Polygon and MultiPolygon geometries are converted.
    - Every row becomes one node.
    - Every GeoDataFrame column is stored as a node attribute.
    - Two polygons are connected if they are spatially adjacent

    Parameters
    ----------
    gdf : GeoDataFrame
    idx : The column name of GeoPanda that to be used as node name

    Returns
    -------
    nx.Graph
    """
    # Defensive Input Check
    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError("Input must be a GeoDataFrame.")

    if idx not in gdf.columns:
        raise ValueError(f"Column '{idx}' does not exist in GeoDataFrame.")

    # Keep polygons only
    gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])].copy()

    # calculate the centroids
    gdf['centroid'] = gdf.centroid

    G = nx.Graph()

    # -------------------------
    # Add nodes
    # -------------------------
    for row_id, row in gdf.iterrows():

        node_name = row[idx]

        attrs = row.to_dict()

        # optional: remove geometry attribute
        attrs.pop("geometry")
        attrs.pop(idx)

        # save centroid coordinate
        attrs["x"] = row.centroid.x
        attrs["y"] = row.centroid.y

        G.add_node(node_name, **attrs)


    # -------------------------
    # Spatial adjacency
    # -------------------------
    sindex = gdf.sindex

    for row_id, geom in enumerate(gdf.geometry):

        node_a = gdf.iloc[row_id][idx]

        candidates = list(
            sindex.intersection(geom.bounds)
        )

        for other_id in candidates:

            if other_id <= row_id:
                continue

            other_geom = gdf.iloc[other_id].geometry

            if geom.touches(other_geom):

                node_b = gdf.iloc[other_id][idx]

                G.add_edge(node_a, node_b)

    return G


if __name__ == "__main__":
    regions = gpd.read_file("data\\Localities_LGATE_234_WA_GDA2020_Public_Geopackage\\Localities_LGATE_234_WA_GDA2020_Public.gpkg")

    # print(regions.info())
    metro = regions[
        regions["postcode"].astype(int).between(6000,6199)
    ]


    #print(metro_mines.head())
    print(metro.info())
    print(metro.head())

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()

    metro.plot(ax=ax,
            facecolor="lightgray",
            edgecolor="black")


    plt.show()


    metro_graph = gdf_to_graph(gdf=metro, idx='name')

    pos = {
        node: (
            data["x"],
            data["y"]
        )
        for node, data in metro_graph.nodes(data=True)
    }

    nx.draw(G=metro_graph,
            pos=pos,
            node_color='C1',
            node_shape='s',
            node_size=5,
            with_labels=False,
            font_size=3)

    plt.axis("equal")
    plt.show()