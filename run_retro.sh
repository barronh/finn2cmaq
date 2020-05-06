#!/bin/bash

STARTDAY=2016-01-01
./scripts/get_retro.py ${STARTDAY}
YYYY=`date -ud "${STARTDAY}" +%Y`
./scripts/txt2daily.py aux/GRIDDESC 108NHEMI2 ${YYYY} bai.acom.ucar.edu/Data/fire/data/FINNv1.5_${YYYY}.GEOSCHEM.tar.gz daily/${YYYY}/FINNv1.5_${YYYY}.GEOSCHEM.nc
./scripts/daily2hourly3d.py daily/${YYYY}/FINNv1.5_${YYYY}.GEOSCHEM.nc hourly/%Y/%m/FINNv1.5_2016.CB6r3.3D.%Y-%m-%d.nc
