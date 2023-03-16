## This script is template to adjust grid values 
## that overlaps filtering areas 

import geopandas as gpd
import glob
import os

if __name__ == '__main__':
    # gdf that contains areas with zero tree height
    flt = gpd.read_file('../data/filter_poly.gpkg', driver='gpkg')

    # path to gridded atl samples
    #path = "/adapt/nobackup/people/jli30/workspace/forest/experiment_2021/scripts/cells"
    path = "/adapt/nobackup/people/jli30/workspace/forest/STG/data/cells_rh90"
    
    # application to single box
    files = glob.glob(os.path.join(path, "sample_*_max.gpkg"))
    ##ff = glob.glob(os.path.join(path, "sample_1315468*.gpkg"))
    for ff in files:
        # construct file name
        fn = os.path.splitext(os.path.basename(ff))[0]
        fn = f"{fn}_zf.gpkg"
        out = os.path.join("../data/cells_rh90_updated", fn)

        print("Proc ",  ff)
        cell =  gpd.read_file(ff, driver='gpkg')
        merged = gpd.sjoin(cell, flt, how='left', op='within')

        # subset of merged that indicating overlaps
        if merged.index_right.notna().sum() > 0 :
            print("Find Overlaps")
            #ol = merged.loc[(merged.index_right.notna()) & (merged.rh90 > 0) ]
            ol = merged.loc[merged.index_right.notna()]
            # update grid values
            cell.loc[ol.index, 'rh90'] = 0.0
            cell.to_file(out, driver="GPKG", layer="boxes")
        else:
            print("No Overlap! Moving On")
            cmd = f'cp {ff} {out}'
            os.system(cmd)

    # write out single box
    # TBA
        


        


