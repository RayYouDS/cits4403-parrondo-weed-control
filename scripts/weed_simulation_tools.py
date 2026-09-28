import numpy as np
from rasterio.features import rasterize
from rasterio.transform import from_bounds


def weed_index_initialize(density, pressure_coef, w_min=0.05, w_max=1.0):
    if w_max < w_min:
        raise ValueError('Max index must greater then min index')
    
    weed_index = w_min + (w_max - w_min) * np.exp(-density*pressure_coef)
    return weed_index


def polygon_to_grid(gdf, cell_size=100, crs="EPSG:7850"):
    """
    Convert polygon GeoDataFrame with weed_index into a NumPy grid.

    Parameters
    ----------
    gdf : GeoDataFrame
        Polygon data containing a 'weed_index' column.
    cell_size : float
        Grid cell size in CRS units (e.g. metres).

    Returns
    -------
    weed_grid : np.ndarray
        2D array containing weed index [0, 1].
        np.nan represents cells outside the study area.
    transform : Affine
        Raster transform.
    
    """

    if "weed_index" not in gdf.columns:
        raise ValueError("GeoDataFrame must contain 'weed_index' column")

    if cell_size <= 0:
        raise ValueError("cell_size must be greater than 0")

    # Reproject to projected CRS
    gdf = gdf.to_crs(crs)

    # Bounding box
    minx, miny, maxx, maxy = gdf.total_bounds

    # Grid dimensions
    width = int(np.ceil((maxx - minx) / cell_size))
    height = int(np.ceil((maxy - miny) / cell_size))

    # Affine transformation
    transform = from_bounds(
        minx,
        miny,
        maxx,
        maxy,
        width,
        height
    )

    # Polygon -> (geometry, weed_index)
    shapes = (
        (geom, value)
        for geom, value in zip(
            gdf.geometry,
            gdf["weed_index"]
        )
        if geom is not None and not geom.is_empty
    )

    # Rasterize
    weed_grid = rasterize(
        shapes=shapes,
        out_shape=(height, width),
        transform=transform,
        fill=np.nan,
        dtype="float32"
    )

    valid_mask = ~np.isnan(weed_grid)

    return weed_grid, valid_mask, transform
