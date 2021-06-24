FINN2CMAQ Processor
-------------------

This processor make Fire Emissions ready for CMAQ.

FINN makes global predictions of fire emissions that are quickly available
as a part of the WACMM system. This processor takes the WACMM FINN input
and converts it to a 2D daily ioapi file. It then converts teh 2D daily file
into a 3D hourly file for use in CMAQ.

The processor can work with retrospective tar.gz files from bai.acom.ucar.edu
or daily near-real-time tz files from www.acom.ucar.edu.

1. Download a daily text file (`./scripts/get.py`)
2. Translate to CMAQ input (`./scripts/txt2daily.py`)
3. Add LAY and hourly (`./daily2hourly3d.py`)

Example:

```
./run_nrt.sh
```

Prerequisites
-------------

- Command-Line (i.e, Linux, Mac)
- Python3
  - pandas
  - numpy
  - PseudoNetCDF

Annotated Directory Structure
-----------------------------

```
.
|-- README.md
|-- run_nrt.sh
|-- run_retro.sh
|-- gc2_to_cb6r3_ae7.txt
|-- examples
|   `-- FINN2CMAQ.ipynb
|-- scripts
|   |-- get_retro.py
|   |-- get_nrt.py
|   |-- txt2daily.py
|   `-- daily2hourly3d.py
|-- aux
|   |-- README.md
|   |-- GRIDDESC
|   |-- layerfrac.csv
|   `-- tpro.txt
|-- daily
|   `-- %Y
|       `-- FINNv1.5_%Y-%m-%d.GEOSCHEM.nc
|-- hourly
|   `-- %Y
|       `-- %m
|           `-- FINNv1.5_%Y.CB6r3.3D.%Y-%m-%d.nc
`-- www.acom.ucar.edu
    |-- Data
    |   `-- fire
    |       `-- data
    |           `-- FINNv1.5_2016.GEOSCHEM.tar.gz
    `-- acresp
        `-- MODELING
            `-- finn_emis_txt
                `-- GLOB_GEOSchem_%Y%j.txt.gz
```
