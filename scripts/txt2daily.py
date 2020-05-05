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


doublere = re.compile('([dD][+-])')
units = defaultdict(lambda: 'moles/day')
units['OC'] = 'kg/day'
units['BC'] = 'kg/day'
units['PM25'] = 'kg/day'
units['AREA'] = 'm**2'
units['longitude'] = 'degrees_east'
units['latitude'] = 'degrees_north'
units['DAY'] = 'day_of_year'
units['HOUR'] = '<HHMM>'


def renamer(k):
    if k == 'LONGI':
        return 'longitude'
    elif k == 'LATI':
        return 'latitude'
    else:
        return k


def process(gf, args):
    path = args.FINNPATH
    gf.SDATE = args.YEAR * 1000 + 1
    gf.TSTEP = 240000
    del gf.variables['TFLAG']
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
    im, jm = gf.ll2ij(df.longitude.values, df.latitude.values, clean='mask')
    i = im.filled(-999)
    j = jm.filled(-999)
    df['I'] = i
    df['J'] = j
    # Remove fires outside the domain or with detects
    # less than 50 m2 -- assumed false detect.
    indf = df.query('I != -999 and J != -999 and AREA >= 50')
    sumdf = indf.groupby(['DAY', 'I', 'J'], as_index=False).sum()
    days = np.arange(sumdf.DAY.min(), sumdf.DAY.max() + 1)
    outf = gf.copy(variables=False, dimensions=True, props=True, data=False)
    outf.createDimension('TSTEP', days.size).setunlimited(True)
    outf.SDATE = args.YEAR * 1000 + days[0]
    refday = days[0]
    varkeys = sumdf.columns
    for varkey in varkeys:
        var = outf.createVariable(varkey, 'f', ('TSTEP', 'LAY', 'ROW', 'COL'))
        var.long_name = varkey.ljust(16)
        var.var_desc = varkey.ljust(80)
        var.units = units[varkey].ljust(16)

    for day in days:
        dayi = day - refday
        daydf = sumdf.query('DAY == {}'.format(day))
        iidx = daydf.I.values
        jidx = daydf.J.values
        kidx = iidx * 0
        tidx = kidx + dayi
        for varkey in varkeys:
            var = outf.variables[varkey]
            var[tidx, kidx, jidx, iidx] = daydf[varkey].values

    if 'TFLAG' in outf.variables:
        del outf.variables['TFLAG']

    outf.updatemeta()
    return outf


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
        outf = process(gf, args)
        outdir = os.path.dirname(args.OUTPATH)
        os.makedirs(outdir, exist_ok=True)
        outf.save(
            args.OUTPATH, format='NETCDF4_CLASSIC',
            complevel=1, verbose=args.verbose
        )
