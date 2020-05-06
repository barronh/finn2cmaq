#!/bin/bash

STARTDAY=2020-01-01
GDNAM=108NHEMI2
for day in {0..121}
do
  YYYYMMDD=`date -ud "${STARTDAY} +${day}days" +%Y-%m-%d`
  YYYY=`date -ud "${YYYYMMDD}" +%Y`
  YYYYJJJ=`date -ud "${YYYYMMDD}" +%Y%j`
  ./scripts/get_nrt.py ${YYYYMMDD}
  ./scripts/txt2daily.py aux/GRIDDESC ${GDNAM} ${YYYY} www.acom.ucar.edu/acresp/MODELING/finn_emis_txt/GLOB_GEOSchem_${YYYYJJJ}.txt.gz daily/${YYYY}/FINNv1.5_${YYYYMMDD}.GEOSCHEM.NRT.${GDNAM}.nc
  ./scripts/daily2hourly3d.py daily/${YYYY}/FINNv1.5_${YYYYMMDD}.GEOSCHEM.NRT.${GDNAM}.nc hourly/%Y/%m/FINNv1.5_2016.CB6r3.NRT.${GDNAM}.3D.%Y-%m-%d.nc
done
