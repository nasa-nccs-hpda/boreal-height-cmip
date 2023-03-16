# script to merge all griddex box into xarray and write out as tiff
import geopandas as gpd
import rioxarray as rxr
import xarray as xr
import numpy as np
import glob
import os

# build xarray dataarray template
bio_file = "/adapt/nobackup/projects/ilab/data/worldclim/1km/bioclim/wc2.0_30s_bio/wc2.0_bio_30s_01.tif"
minlon = -170.0
maxlon = -45.0 
minlat = 40
maxlat = 75
raster =  rxr.open_rasterio(bio_file).rio.clip_box(minlon, minlat, maxlon, maxlat)
xx = xr.zeros_like(raster)+np.nan
lons = xx.x.values
lats = xx.y.values
print(xx.shape)
# read one gridded box as example (200 x 200 box)
# Here should be a loop
#files = glob.glob(os.path.join("../data/cells_rh90_updated", "sample*_max_zf.gpkg"))
files = glob.glob(os.path.join("../data/cells_updated", "sample*_zf.gpkg"))

##cfn = '/adapt/nobackup/people/jli30/workspace/forest/experiment_2021/scripts/cells/sample_1315468.gpkg'
rm_list = ['547427', '546902', '1642603', '1642752', '457077', '389261', '1813851']

for cfn in files: 
    print("Proc ", cfn)
    ids = os.path.basename(cfn).split('_')[1]
    cell = gpd.read_file(cfn, driver='gpkg')
    # get bounding box
    bnd = cell.total_bounds
    xs = np.argmin(np.abs(lons-bnd[0]))
    ys = np.argmin(np.abs(lats-bnd[1]))
    #xs = list(lons).index(bnd[0])
    #ys = list(lats).index(bnd[1])
    ## alternative 
    ##
    ## index = np.argmin(np.abs(np.array(a)-11.5))
    ##
    h_arr = cell['h_can'].values
    if ids in rm_list:
        print(ids)
        h_arr = np.where(h_arr>0, 0, h_arr)
    print(np.nanmax(h_arr), np.nanmin(h_arr))

    nv = np.count_nonzero(~np.isnan(h_arr))
    print("Valid Samples in cell : ", nv)
    xx.data[0, ys-200:ys, xs:xs+200] = np.transpose(h_arr.reshape((200, 200)))
    xv = np.count_nonzero(~np.isnan(xx.values))
    print("Valid Samples in data array : ", xv)


# write out
# construct fn
fn = "../data/hcan_update_zeroglnd_fillzeros.tif"
xx.rio.to_raster(fn)

