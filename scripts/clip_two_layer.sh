#!/bin/bash

module purge
module load gdal
module list

#vname=UiO_PEX_PERPROB_3.0_20171201_2000_2016_warp
#alg=average
vname=BDTICM_M_250m_warp
alg=mode
infile=/adapt/nobackup/people/pmontesa/userfs02/projects/3dsi/stacks/${vname}.tif

#gdalwarp -te -170.0 40.0 -45.0 75.0 -tr 0.008333333333333333 -0.008333333333333333 -r ${alg} ${infile} ./${vname}_clip.tif 
gdalwarp -te -170.0 40.0 -45.0 75.0 -tr 0.041666666666666664 -0.041666666666666664 -r ${alg} -ot Float32 ${infile} ./${vname}_clip_25min.tif 
