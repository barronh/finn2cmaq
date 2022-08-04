FINN2CMAQ Processor
===================

Overview
--------

This processor make Fire Emissions ready for CMAQ.

FINN makes global predictions of fire emissions that are quickly available
as a part of the WACMM system. This processor takes the WACMM FINN input
and converts it to a 2D daily ioapi file. It then converts the 2D daily file
into a 3D hourly file for use in CMAQ. It should be noted that this 3D product
is a very simplistic version of fires.

The processor can work with retrospective tar.gz files from bai.acom.ucar.edu
or daily near-real-time tz files from www.acom.ucar.edu.

1. Download a daily text file (`./scripts/get.py`)
2. Translate to CMAQ input (`./scripts/txt2daily.py`)
3. Add LAY and hourly (`./daily2hourly3d.py`)

Example:

See examples/FINN2CMAQ.ipynb

Notable Updates
---------------

* 2022-08-04
  * Versions have been added to txt2daily.py and daily2hourly3d.py scripts. (0.1.0)
  * Histories including versions have been added to outputs.
  * Additional documentation has been added to functions.
* 2021-06-24
  * An example Jupyter Notebook has been added for testing purposes.
  * The PM speciation has been updated to use g/s definitions.
  * The `scripts/daily2hourly3d.py` has been updated to output a CMAQ-ready unit and to have the option to process individual days.


Prerequisites
-------------

- Command-Line (i.e, Linux, Mac)
- Python3
  - pandas
  - numpy
  - pyproj
  - PseudoNetCDF

Annotated Directory Structure
-----------------------------

```
.
|-- README.md
|   # This file
|-- run_nrt.sh
|   # A wrapper to run 1 day for the near-real-time FINN
|-- run_retro.sh
|   # A wrapper to run 1 year for the retrospective FINN
|-- examples
|   `-- FINN2CMAQ.ipynb
|-- scripts
|   |-- get_retro.py
|   |-- get_nrt.py
|   |-- txt2daily.py
|   `-- daily2hourly3d.py
|-- aux
|   |-- README.md
|   |   # More details about aux files
|   |-- gc2_to_cb6r3_ae7.txt
|   |   # speciation definition.
|   |-- GRIDDESC
|   |   # example grid definitions
|   |-- layerfrac.csv
|   |   # example layer fractions
|   `-- tpro.txt
|       # example hour fractions
|-- daily
|   `-- %Y
|       |-- FINNv1.5_%Y.GEOSCHEM.nc
|       |   # file and folder only exist if run_retro.sh has been run
|       `-- FINNv1.5_%Y-%m-%d.GEOSCHEM.NRT.108NHEMI2.nc
|           # file and folder only exist if run_nrt.sh has been run
|-- hourly
|   `-- %Y
|       `-- %m
|           |-- FINNv1.5_%Y.CB6r3.3D.%Y-%m-%d.nc
|           |   # file and folders only exist if run_retro.sh have been run
|           `-- FINNv1.5_%Y.CB6r3.3D.%Y-%m-%d.nc
|               # file and folders only exist if run_nrt.sh have been run
`-- www.acom.ucar.edu
    |-- Data
    |   `-- fire
    |       `-- data
    |           `-- finn1
    |               `-- FINNv1.5_2016.GEOSCHEM.tar.gz
    |                   # file and folders only exist if run_retro.sh has been run
    `-- acresp
        `-- MODELING
            `-- finn_emis_txt
                `-- GLOB_GEOSchem_%Y%j.txt.gz
                    # file and folders only exist if run_nrt.sh has been run
```
