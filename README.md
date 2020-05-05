CMAQ Fire INveNtory (FINN) Processor
------------------------------------

FINN makes global predictions of fire emissions that are quickly available
as a part of the WACMM system. This processor takes the WACMM FINN input
and converts it to a 2D daily ioapi file. It then converts teh 2D daily file
into a 3D hourly file for use in CMAQ.

1. Download a daily text file (`./scripts/get.py`)
2. Translate to CMAQ input (`./scripts/txt2daily.py`)
3. Add LAY and hourly (`./daily2hourly3d.py Translate to CMAQ input (`./txt2ioapi.py GRIDDESC <GDNAM> <downloadedpath>

Example:
```
./run.sh
./scripts/get.py 2019-01-01
./scripts/txt2dialy.py GRIDDESC 108NHEMI2 2019 www.acom.ucar.edu/acresp/MODELING/finn_emis_txt/GLOB_GEOSchem_2019001.txt.gz daily/FINNv1.5_2019-01-01.GEOSCHEM.nc
./scripts/daily2hourly3d.py daily/FINNv1.5_2019-01-01.GEOSCHEM.nc hourly/2019/01/FINNv1.5_2016.CB6r3.3D.2019-01-01.nc
```

Annotated Directory Structure
-----------------------------

```
.
|-- GRIDDESC -> /home/bhenders/GRIDDESC
|-- README.md
|-- daily2hourly3d.py
|-- gc2_to_cb6r3_ae7.txt
|-- scripts
|   |-- get.py
|   |-- 
|-- get.py
|-- daily
|   `-- %Y
|       `-- FINNv1.5_%Y-%m-%d.GEOSCHEM.nc
|-- hourly
|   `-- %Y
|       `-- %m
|           `-- FINNv1.5_%Y.CB6r3.3D.%Y-%m-%d.nc
|-- layerfrac.csv
|-- tpro.txt
|-- txt2daily.py
|-- bai.acom.ucar.edu
|   `-- Data
|       `-- fire
|           `-- data
|               `-- FINNv1.5_2016.GEOSCHEM.tar.gz
`-- www.acom.ucar.edu
    `-- acresp
        `-- MODELING
            `-- finn_emis_txt
                `-- GLOB_GEOSchem_%Y%j.txt.gz
```
