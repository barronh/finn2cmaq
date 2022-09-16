#!/usr/bin/env python
# coding: utf-8
import io
import re
import os
import tarfile
import gzip
import argparse
from collections import defaultdict
import pandas as pd
import numpy as np
import PseudoNetCDF as pnc

__version__ = '0.1.0'
__doc__ = """
Use daily2hourly3d.daily2hourly3d to convert daily FINN files to hourly files
that are CMAQ-ready.

Changes:
* 2020-08-04: BHH added version, documentation, and cleaned-up metadata.
"""


doublere = re.compile('([dD][+-])')
units = defaultdict(lambda: 'moles/day')
units['DAY'] = 'day_of_year'
units['TIME'] = '<HHMM>'
units['HOUR'] = '<HHMM>'
units['longitude'] = 'degrees_east'
units['latitude'] = 'degrees_north'
units['POLYID'] = 'none'
units['FIREID'] = 'none'
units['AREA'] = 'm**2'
units['BMASS'] = 'kg/m**2'
units['OC'] = 'kg/day'
units['BC'] = 'kg/day'
units['PM25'] = 'kg/day'
units['PM10'] = 'kg/day'
units['TPC'] = 'kg/day'
units['TPM'] = 'kg/day'
units['NMOC'] = 'kg/day'
units['NMHC'] = 'kg/day'


def renamer(k):
    """
    Arguments
    ---------
    k : str
        Any string

    Returns
    -------
    k : str
        LONGI and LATI are converted to longitude and latitude; all else are
        returned unchanged
    """
    if k == 'LONGI':
        return 'longitude'
    elif k == 'LATI':
        return 'latitude'
    else:
        return k.strip()


def openfinn(path):
    if path.endswith('.tar.gz'):
        with tarfile.open(path, "r:*") as tar:
            csv_path = [
                path for path in tar.getnames() if not path.endswith('.pdf')
            ][0]
            tf = tar.extractfile(csv_path)
            df = pd.read_csv(tf, index_col=False)
    elif path.endswith('.gz'):
        gfile = gzip.GzipFile(path, mode='r')
        dattxt = gfile.read().decode('latin1')
        dattxt = dattxt.replace('D+', 'e+').replace('D-', 'e-')
        dattxt = dattxt.replace('d+', 'e+').replace('d-', 'e-')
        df = pd.read_csv(io.StringIO(dattxt), index_col=False)
    else:
        df = pd.read_csv(path, skipinitialspace=True)

    df.columns = [renamer(k) for k in df.columns]
    return df


def txt2daily(gf, YEAR, FINNPATH, OUTPATH, verbose=0):
    """
    Takes FINN inputs and converts to IOAPI-like daily 2d file.
    * Omits fires less than 50m**2 assuming a misdetect

    Arguments
    ---------
    gf : NetCDF-like file
        Template for gridded file
    YEAR : int
        Year for output file
    FINNPATH : str
        Path to finn input. Can be .tar.gz or .gz or .csv
    OUTPATH : str
        Output path for the NetCDF IOAPI-like file. Or None for no save.
    verbose : int
        Level of verbosity

    Returns
    -------
    outf : NetCDF-like file
        PseudoNetCDF if OUTPATH is None; NetCDF otherwise.
    """
    meanvars = ['GENVEG', 'TIME']
    gf.SDATE = YEAR * 1000 + 1
    gf.TSTEP = 240000
    del gf.variables['TFLAG']
    df = openfinn(FINNPATH)
    im, jm = gf.ll2ij(df.longitude.values, df.latitude.values, clean='mask')
    i = im.filled(-999)
    j = jm.filled(-999)
    df['I'] = i
    df['J'] = j
    # Remove fires outside the domain or with detects
    # less than 50 m2 -- assumed false detect.
    # BHH: I did not come up with this, but I do not recall who suggested it.
    indf = df.query('I != -999 and J != -999 and AREA >= 50')
    gdf = indf.groupby(['DAY', 'I', 'J'], as_index=False)
    sumdf = gdf.sum()
    meandf = gdf.mean()
    days = np.arange(sumdf.DAY.min(), sumdf.DAY.max() + 1)
    outf = gf.copy(variables=False, dimensions=True, props=True, data=False)
    outf.createDimension('TSTEP', days.size).setunlimited(True)
    outf.SDATE = YEAR * 1000 + days[0]
    refday = days[0]
    varkeys = sumdf.columns
    for varkey in varkeys:
        var = outf.createVariable(varkey, 'f', ('TSTEP', 'LAY', 'ROW', 'COL'))
        var.long_name = varkey.ljust(16)
        var.var_desc = varkey.ljust(80)
        var.units = units[varkey].ljust(16)

    for day in days:
        dayi = day - refday
        daysumdf = sumdf.query('DAY == {}'.format(day))
        daymeandf = meandf.query('DAY == {}'.format(day))
        iidx = daysumdf.I.values
        jidx = daysumdf.J.values
        kidx = iidx * 0
        tidx = kidx + dayi
        for varkey in varkeys:
            var = outf.variables[varkey]
            if varkey in meanvars:
                val = daymeandf[varkey].values
            else:
                val = daysumdf[varkey].values
            var[tidx, kidx, jidx, iidx] = val

    if 'TFLAG' in outf.variables:
        del outf.variables['TFLAG']
        setattr(
            outf, 'VAR-LIST', ''.join([varkey.ljust(16) for varkey in varkeys])
        )

    if 'nv' in outf.dimensions:
        del outf.dimensions['nv']
    if 'tnv' in outf.dimensions:
        del outf.dimensions['tnv']
    if hasattr(outf, 'Conventions'):
        delattr(outf, 'Conventions')
    outf.updatemeta()
    outf.variables.move_to_end('TFLAG', last=False)
    history = (
        "Converted to daily 2D IOAPI-like file from "
        + f"{FINNPATH} using txt2daily (v{__version__})"
    ).ljust(60*80)[:60*80]
    filedesc = (
        "FINN emissions as surface-level daily files with species and units"
        + " from the file"
    ).ljust(60*80)[:60*80]
    outf.UPNAM = "txt2daily".ljust(16)
    outf.FILEDESC = filedesc
    outf.HISTORY = history
    outdir = os.path.dirname(OUTPATH)
    os.makedirs(outdir, exist_ok=True)
    if OUTPATH is None:
        return outf
    else:
        diskf = outf.save(
            OUTPATH, format='NETCDF4_CLASSIC',
            complevel=1, verbose=verbose
        ).close()
        return diskf


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', default=0, action='count')
    parser.add_argument('GRIDDESC')
    parser.add_argument('GDNAM')
    parser.add_argument('YEAR', type=int)
    parser.add_argument('FINNPATH')
    parser.add_argument('OUTPATH')
    args = parser.parse_args()
    if os.path.exists(args.OUTPATH):
        print('Keeping cached', args.OUTPATH)
    else:
        gf = pnc.pncopen(args.GRIDDESC, format='griddesc', GDNAM=args.GDNAM)
        outf = txt2daily(
            gf, args.YEAR, args.FINNPATH, args.OUTPATH, args.verbose
        )
