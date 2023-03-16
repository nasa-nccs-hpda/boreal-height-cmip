## The script to generate a set of "circles" to indicate areaes that have 0 tree height
from functools import partial

import pyproj
from shapely import geometry
from shapely.geometry import Point
from shapely.ops import transform
import geopandas as gpd

def gen_circle(center, radius):
    #center: tuple (lat, lon)
    #radius: unit m
    #return:
    #    polygon
    lat = center[0]
    lon = center[1]
    
    local_azimuthal_projection = "+proj=aeqd +R=6371000 +units=m +lat_0={} +lon_0={}".format(lat, lon)
    wgs84_to_aeqd = partial(
                    pyproj.transform,
                    pyproj.Proj("+proj=longlat +datum=WGS84 +no_defs"),
                    pyproj.Proj(local_azimuthal_projection),
                    )
    aeqd_to_wgs84 = partial(
                    pyproj.transform,
                    pyproj.Proj(local_azimuthal_projection),
                    pyproj.Proj("+proj=longlat +datum=WGS84 +no_defs"),
                    )

    center = Point(float(lon), float(lat))
    point_transformed = transform(wgs84_to_aeqd, center)
    buffer = point_transformed.buffer(radius)
    # Get the polygon with lat lon coordinates
    circle_poly = transform(aeqd_to_wgs84, buffer)
    return circle_poly


if __name__ == '__main__':
    # main 
    rd_lookup = {"nunavut": 50000,
                "north slope" : 20000,
                "brooks range" : 10000,
                "mtn galciers" : 3000,
                "nrn qc" : 20000}

    lc_lookup = {"nunavut": [(65.37705465422397, -101.40355492533581), (65.65456692902411, -92.40262707558485)],
                    "north slope" :  [(70.46537715531564, -156.24159495849852), (70.46537715531564, -156.24159495849852)],
                    "brooks range" : [(68.866779376079, -152.3005433253658), (67.79514739601498, -154.88370834255306)],
                    "mtn galciers" : [(63.0499763289837, -150.92024591570194), (61.399418356237256, -146.99218658810787), (60.660913822091636, -143.654390423891)],
                    "nrn qc" : [(61.568329584048875, -74.94199403897278), (62.10561286073038, -77.11023664252646)]}
    
    geoms = []
    for key, item in lc_lookup.items():
        rdius = rd_lookup[key]
        for cntr in item:
            c = gen_circle(cntr, rdius)
            geoms.append(c)
            print("rgn ", key, "r ", rdius, "cnt ", cntr )
    gdf = gpd.GeoDataFrame(geoms, columns=['geometry'], crs='EPSG:4326')
    gdf.to_file('filter_circles.gpkg', layer='', driver="GPKG")