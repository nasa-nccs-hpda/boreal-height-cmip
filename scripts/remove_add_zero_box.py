import rioxarray as rxr
import geopandas as gpd
from shapely.geometry import box

def create_cells(xarr, yarr, cell_sz):
    grid_cells = []
    for x0 in xarr:
        for y0 in yarr:
            x1 = x0+cell_sz
            y1 = y0+cell_sz
            grid_cells.append(box(x0, y0, x1, y1))
    return gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs='EPSG:4326')

# create 2 box with zeros
biofn = "/adapt/nobackup/projects/ilab/data/worldclim/1km/bioclim/wc2.0_30s_bio/wc2.0_bio_30s_02.tif"
ds = rxr.open_rasterio(biofn)
csize = ds.rio.resolution()[0] # cell size of raster
lons = ds.x.values
lats = ds.y.values

npix = 100
pts = (-97.2245, 69.0451)
pick = ds.sel(x=pts[0], y=pts[1], method='nearest')
xid = list(lons).index(pick.x.values)
yid = list(lats).index(pick.y.values)

xs = lons[(xid-npix):(xid+npix)]
ys = lats[(yid-npix):(yid+npix)]

cell = create_cells(xs, ys, csize)
cell['h_can'] = 0.0

cell.to_file(f"../data/cells_updated/sample_3_zf.gpkg", layer="cell", driver="GPKG")