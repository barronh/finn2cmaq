#!/bin/bash

./scripts/get.py 2019-01-01
./scripts/txt2daily.py aux/GRIDDESC 108NHEMI2 2019 www.acom.ucar.edu/acresp/MODELING/finn_emis_txt/GLOB_GEOSchem_2019001.txt.gz daily/2019/FINNv1.5_2019-01-01.GEOSCHEM.nc
./scripts/daily2hourly3d.py daily/2019/FINNv1.5_2019-01-01.GEOSCHEM.nc hourly/%Y/%m/FINNv1.5_2016.CB6r3.3D.%Y-%m-%d.nc
