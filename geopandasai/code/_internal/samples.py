SAMPLES = '''
# The following examples illustrate multiple examples of using geopandas. In all of them,
# consider that the used variables are just for illustration. Before adapting them to my code, replace them with
# my variables.

# One commonly used GIS task is to be able to find the nearest neighbor. For instance, you might have a single Point object representing your home location, and then another set of locations representing e.g. public transport stops. Then, quite typical question is “which of the stops is closest one to my home?” This is a typical nearest neighbor analysis, where the aim is to find the closest geometry to another geometry.
# In Python this kind of analysis can be done with shapely function called nearest_points() that returns a tuple of the nearest points in the input geometries.


from shapely.ops import nearest_points


def _nearest(row, df1, df2, geom1='geometry', geom2='geometry', df2_column=None):
    """Find the nearest point and return the corresponding value from specified column."""

    # create object usable by Shapely
    geom_union = df2.unary_union

    # Find the geometry that is closest
    nearest = df2[geom2] == nearest_points(row[geom1], geom_union)[1]
    # Get the corresponding value from df2 (matching is based on the geometry)
    if df2_column is None:
        value = df2[nearest].index[0]
    else:
        value = df2[nearest][df2_column].values[0]
    return value


def nearest(df1, df2, geom1_col='geometry', geom2_col='geometry', df2_column=None):
    """Find the nearest point and return the corresponding value from specified column.
    :param df1: Origin points of type geopandas.GeoDataFrame
    :param df2: Destination points
    :type df2: geopandas.GeoDataFrame
    :param geom1_col: name of column holding coordinate geometry, defaults to 'geometry'
    :type geom1_col: str, optional
    :param geom2_col: name of column holding coordinate geometry, defaults to 'geometry'
    :type geom2_col: str, optional
    :param df2_column: column name to return from df2, defaults to None
    :type df2_column: str, optional
    :return: df1 with nearest neighbor index or df2_column appended
    :rtype: geopandas.GeoDataFrame
    """
    df1['nearest_id'] = df1.apply(_nearest, df1=df1, df2=df2,
                                  geom1=geom1_col, geom2=geom2_col,
                                  df2_column=df2_column, axis=1)
    return df1

############################################################
# We can use the dissolve function in GeoPandas, which is the spatial version of groupby in pandas. We use dissolve instead of groupby because the former also groups and merges all the geometries (in this case, census tracts) within a given group (in this case, counties).

# Dissolve and group the census tracts within each county and aggregate all the values together
# Source: https://geopandas.org/docs/user_guide/aggregation_with_dissolve.html
va_poverty_county = va_poverty_tract.dissolve(by = 'COUNTYFP', aggfunc = 'sum')


############################################################
# Clip Spatial Polygons. We will clip the Bay Area counties polygon to our created rectangle polygon.
# Countries is a geodataframe, and poly is a shapely polygon used in clipping.

clip_counties = gpd.clip(counties, poly)

############################################################
# If we’re trying to select features that have a specified spatial relationship with another geopandas object, it gets a little tricky. This is because the geopandas spatial relationship functions verify the spatial relationship either row by row or index by index. In other words, the first row in the first dataset will be compared with the corresponding row or index in the second dataset, the second row in the first dataset will be compared with the corresponding row or index in the second dataset, and so on. [6], [7]
# As a result, the number of rows need to correspond or the indices numbers need to match between the two datasets–or else we’ll get a warning and the output will be empty.
# Because each record in a GeoDataFrame has a geometry column that stores that record’s geometry as a shapely object, we can call this object if we want to check a bunch of features against one extent (with one geometry). [6], [7]

# Select the Santa Clara County boundary
sc_county = counties[counties["coname"] == "Santa Clara County"]

# Subset the GeoDataFrame by checking which wells are within Santa Clara County's Shapely object
wells_within_sc_shapely = wells[wells.within(sc_county.geometry.values[0])]

############################################################
#  The Python module called OSMnx that can be used to retrieve, construct, analyze, and visualize street networks from OpenStreetMap, and also retrieve data about Points of Interest such as restaurants, schools, and lots of different kind of services.

# import osmnx
import osmnx as ox
import geopandas as gpd

# Specify the name that is used to seach for the data
place_name = "Edgewood Washington, DC, USA"
# Get place boundary related to the place name as a geodataframe
area = ox.geocode_to_gdf(place_name)

############################################################
# It is possible to retrieve other types of OSM data features with OSMnx such as buildings or points of interest (POIs). Let’s download the buildings with ox.features_from_place docs function and plot them on top of our street network in Kamppi.

# List key-value pairs for tags
tags = {'building': True}

buildings = ox.features_from_place(place_name, tags)

############################################################
# Favor plotting geopandasai dataframes with Folium. Folium builds on the data wrangling strengths of the
# Python ecosystem and the mapping strengths of the leaflet.js library.
# This allows you to manipulate your data in Geopandas and visualize it on a Leaflet map via Folium.

############################################################
# Folium has a number of built-in tilesets from OpenStreetMap, Mapbox, and CartoDB. For common data
# exploration, favor raster tiles as they are faster to load. For example

map = folium.Map(location=[13.406, 80.110], tiles="OpenStreetMap", zoom_start=9)

# For high quality visualization and for print maps,
# favor vector tiles, e.g., OpenStreetMap vector tiles, as they don't distort with the zoom. For example:

OSM vector tiles. Here is the python code snippet:

    vector_tile_url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    vector_tile_attr = "OpenStreetMap"

    # Add vector tiles as the base layer
    fl.TileLayer(
        tiles=vector_tile_url,
        attr=vector_tile_attr,
        name="Vector Tiles",
        overlay=False,
        control=True
    ).add_to(map_indiv_lines)

#######################################################
# Add markers
# To represent the different types of volcanoes, you can create Folium markers and add them to your map.

# Create a geometry list from the GeoDataFrame
geo_df_list = [[point.xy[1][0], point.xy[0][0]] for point in geo_df.geometry]

# Iterate through list and add a marker for each volcano, color-coded by its type.
i = 0
for coordinates in geo_df_list:
    # assign a color marker for the type of volcano, Strato being the most common
    if geo_df.Type[i] == "Stratovolcano":
        type_color = "green"
    elif geo_df.Type[i] == "Complex volcano":
        type_color = "blue"
    elif geo_df.Type[i] == "Shield volcano":
        type_color = "orange"
    elif geo_df.Type[i] == "Lava dome":
        type_color = "pink"
    else:
        type_color = "purple"

    # Place the markers with the popup labels and data
    map.add_child(
        folium.Marker(
            location=coordinates,
            popup="Year: "
            + str(geo_df.Year[i])
            + "<br>"
            + "Name: "
            + str(geo_df.Name[i])
            + "<br>"
            + "Country: "
            + str(geo_df.Country[i])
            + "<br>"
            + "Type: "
            + str(geo_df.Type[i])
            + "<br>"
            + "Coordinates: "
            + str(geo_df_list[i]),
            icon=folium.Icon(color="%s" % type_color),
        )
    )
    i = i + 1

#######################################################
# Folium Heatmaps
# Folium is well known for its heatmaps, which create a heatmap layer. To plot a heatmap in Folium, you need a list of latitudes and longitudes.

# This example uses heatmaps to visualize the density of volcanoes
# which is more in some parts of the world compared to others.

from folium import plugins

map = folium.Map(location=[15, 30], tiles="Cartodb dark_matter", zoom_start=2)

heat_data = [[point.xy[1][0], point.xy[0][0]] for point in geo_df.geometry]

heat_data
plugins.HeatMap(heat_data).add_to(map)

map

#######################################################
# Plotting polygons with Folium
# An example which overlays the boundaries of boroughs on map with borough name as popup:

for _, r in df.iterrows():
    # Without simplifying the representation of each borough,
    # the map might not be displayed
    sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": "orange"})
    folium.Popup(r["BoroName"]).add_to(geo_j)
    geo_j.add_to(m)
m

#######################################################
# Compute polygon centroid.
# In order to properly compute geometric properties, in this case centroids, of the geometries,
# we need to project the data to a projected coordinate system.

# Project to NAD83 projected crs
df = df.to_crs(epsg=2263)

# Access the centroid attribute of each polygon
df["centroid"] = df.centroid

#######################################################
# In order to display geometry data in the Folium map, and the data is found in a project CRS, we need to project
# the geometry back to a geographic coordinate system with latitude and longitude values, i.e., CRS= 4326.

# Project to WGS84 geographic crs

# geometry (active) column
df = df.to_crs(epsg=4326)

# Centroid column
df["centroid"] = df["centroid"].to_crs(epsg=4326)

#######################################################
# Add centroid markers to the map

for _, r in df.iterrows():
    lat = r["centroid"].y
    lon = r["centroid"].x
    folium.Marker(
        location=[lat, lon],
        popup="length: {} <br> area: {}".format(r["Shape_Leng"], r["Shape_Area"]),
    ).add_to(m)

m

#######################################################
# Spatial Joins
# A spatial join uses binary predicates such as intersects and crosses to combine two GeoDataFrames based on
# the spatial relationship between their geometries.
# A common use case might be a spatial join between a point layer and a polygon layer where you want to retain
# the point geometries and grab the attributes of the intersecting polygons.


#######################################################
# Spatial Joins between two GeoDataFrames
# Assume pointdf is a geopandas dataframe that has point geometries, and polydf has polygon geometries

# Left outer join. Note the NaNs where the point did not intersect a polygon
join_left_df = pointdf.sjoin(polydf, how="left")

# Right outer join.  We keep all rows from the right and duplicate them if necessary to represent multiple
# hits between the two dataframes.
join_right_df = pointdf.sjoin(polydf, how="right")

# Inner join. Note the lack of NaNs; dropped anything that didn't intersect
join_inner_df = pointdf.sjoin(polydf, how="inner")

# We’re not limited to using the intersection binary predicate. Any of the Shapely geometry methods that return a Boolean can be used by specifying the predicate kwarg.
pointdf.sjoin(polydf, how="left", predicate="within")

# We can also conduct a nearest neighbour join with sjoin_nearest.

pointdf.sjoin_nearest(polydf, how="left", distance_col="Distances")
# Note the optional Distances column with computed distances between each point
# and the nearest polydf geometry.


#######################################################
# CRS
# It’s important that you know the coordinate reference system (CRS) that your data is projected in.
# Many times, data loaded from shapefiles (or other vector formats) have their CRS embedded;
# loading these data using geopandas will make the CRS available in the .crs attribute of the
# GeoDataFrame (e.g. data.crs). Geopandas expresses CRSs as EPSG codes.
'''
