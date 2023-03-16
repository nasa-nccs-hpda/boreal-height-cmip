import rioxarray as rxr
import geopandas as gpd
from shapely.geometry import box
import glob
import os
import numpy as np

def create_cells(xarr, yarr, cell_sz):
    grid_cells = []
    for x0 in xarr:
        for y0 in yarr:
            x1 = x0+cell_sz
            y1 = y0+cell_sz
            grid_cells.append(box(x0, y0, x1, y1))
    return gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs='EPSG:4326')

def get_index():
    files = glob.glob('../data/cells_updated/*.gpkg')
    idx = [int(os.path.basename(f).split('_')[1]) for f in files]
    return idx

idx = get_index()
# get points from atl08 gdf
n_spl = 500
fn = "/adapt/nobackup/people/jli30/workspace/forest/STG/data/atl08_2020_filtered.parquet"
c_gdf = gpd.read_parquet(fn)
print("Read Atl08 Completed")

#pts = c_gdf['geometry'].sample(n_spl)
pts = c_gdf['geometry'][idx]

# get lons/lats from bioclim
biofn = "/adapt/nobackup/projects/ilab/data/worldclim/1km/bioclim/wc2.0_30s_bio/wc2.0_bio_30s_02.tif"
ds = rxr.open_rasterio(biofn)
csize = ds.rio.resolution()[0] # cell size of raster

lons = ds.x.values
lats = ds.y.values


npix = 100 # buffer size (index) for x/y axis
p90_fun = lambda x: np.percentile(x, q=90)

for i in range(len(idx)):
    print(f"Processing #{i} of {n_spl}")
    # extract point coord
    tx = pts.iloc[i].x
    ty = pts.iloc[i].y

    # find pixel id in raster
    pick = ds.sel(x=tx, y=ty, method='nearest')
    xid = list(lons).index(pick.x.values)
    yid = list(lats).index(pick.y.values)
    # extract list of x & y
    xs = lons[(xid-npix):(xid+npix)]
    ys = lats[(yid-npix):(yid+npix)]

    cell = create_cells(xs, ys, csize)
    cell_max = cell.copy()
   

    # subset gdf
    gdf_sub = c_gdf[['rh90', 'geometry']].cx[(xs[0]-2.0):(xs[-1]+2.0), (ys[0]-2.0):(ys[-1]+2.0)]
    merged = gpd.sjoin(gdf_sub, cell, how='left', op='within')
    dissolve_p90 = merged.dissolve(by='index_right', aggfunc=p90_fun)
    dissolve_max = merged.dissolve(by='index_right', aggfunc='max')

    
    cell.loc[dissolve_p90.index, 'rh90'] = dissolve_p90['rh90'].values
    cell_max.loc[dissolve_max.index, 'rh90'] = dissolve_max['rh90'].values

    # write cell out
    cell.to_file(f"../data/cells_rh90/sample_rh90_{pts.index[i]}_p90.gpkg", layer="cell", driver="GPKG")
    cell_max.to_file(f"../data/cells_rh90/sample_rh90_{pts.index[i]}_max.gpkg", layer="cell", driver="GPKG")



