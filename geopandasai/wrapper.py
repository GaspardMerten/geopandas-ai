import geopandas as gpd

from .geodataframe_ai import GeoDataFrameAI


def read_file(
        filename: str,
        *args,
        **kwargs,
) -> GeoDataFrameAI:
    """
    Read a vector file (shapefile, GeoJSON, etc.) and return a GeoDataFrameAI.
    """
    return GeoDataFrameAI(gpd.read_file(filename, *args, **kwargs))


def read_parquet(
        path: str,
        *args,
        **kwargs,
) -> GeoDataFrameAI:
    """
    Read a Parquet file and return a GeoDataFrameAI.
    """
    return GeoDataFrameAI(gpd.read_parquet(path, *args, **kwargs))


def read_feather(
        path: str,
        *args,
        **kwargs,
) -> GeoDataFrameAI:
    """
    Read a Feather file and return a GeoDataFrameAI.
    """
    return GeoDataFrameAI(gpd.read_feather(path, *args, **kwargs))


def read_postgis(
        sql: str,
        con,
        *args,
        **kwargs,
) -> GeoDataFrameAI:
    """
    Read data from a PostGIS-enabled database and return a GeoDataFrameAI.
    """
    return GeoDataFrameAI(gpd.read_postgis(sql, con, *args, **kwargs))


def read_fileobj(
        fileobj,
        *args,
        **kwargs,
) -> GeoDataFrameAI:
    """
    Read a file-like object and return a GeoDataFrameAI.
    """
    return GeoDataFrameAI(gpd.read_file(fileobj, *args, **kwargs))


def read_arrow(
        source,
        *args,
        **kwargs,
) -> GeoDataFrameAI:
    """
    Read Arrow (e.g. pyarrow.Table) data and return a GeoDataFrameAI.
    """
    return GeoDataFrameAI(gpd.read_arrow(source, *args, **kwargs))


# Fonctions d’écriture
def to_parquet(
        gdf: GeoDataFrameAI,
        path: str,
        *args,
        **kwargs,
) -> None:
    """
    Write a GeoDataFrameAI to a Parquet file.
    """
    gdf.to_parquet(path, *args, **kwargs)


def to_feather(
        gdf: GeoDataFrameAI,
        path: str,
        *args,
        **kwargs,
) -> None:
    """
    Write a GeoDataFrameAI to a Feather file.
    """
    gdf.to_feather(path, *args, **kwargs)


def to_file(
        gdf: GeoDataFrameAI,
        filename: str,
        *args,
        **kwargs,
) -> None:
    """
    Write a GeoDataFrameAI to a file (shapefile, GeoPackage, GeoJSON, etc.).
    """
    gdf.to_file(filename, *args, **kwargs)


def to_postgis(
        gdf: GeoDataFrameAI,
        name: str,
        con,
        *args,
        **kwargs,
) -> None:
    """
    Write a GeoDataFrameAI to a PostGIS-enabled database.
    """
    gdf.to_postgis(name, con, *args, **kwargs)
