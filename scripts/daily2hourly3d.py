#!/usr/bin/env python
import numpy as np
import pandas as pd
import PseudoNetCDF as pnc
import gc
import os
import argparse


__version__ = '0.1.0'
__doc__ = """
Use daily2hourly3d.daily2hourly3d to convert daily FINN files to hourly files
that are CMAQ-ready.

Changes:
* 2020-08-04: BHH added version, documentation, and cleaned-up metadata.
"""


def getvertical(path):
    """
    Arguments
    ---------
    path : str
        Must have "frac", "sigma_bottom", and "sigma_top" columns. "frac"
        alloates emissions fractionally to vertical levels. "sigma_bottom" and
        "sigma_top" define the vertical coordinate of the bottom and top of
        each layer.

    Returns
    -------
    vglvls, frac : arrays
        vglvls is a 1d array (n+1) of vertical coordinate edges
        frac is a 1d array (n) of vertical fractions
    """
    layerfrac = pd.read_csv(path)
    vglvls = np.array(layerfrac['sigma_bottom'].values, dtype='f')
    vglvls = np.append(vglvls, layerfrac['sigma_top'].values[-1])
    return vglvls, layerfrac['frac'].values


def gettemporal(path, gf):
    """
    Arguments
    ---------
    path : str
        Must have hour1..hour24 fields for local time.

    Returns
    -------
    tfactorarr : array
        Factor matrix to multiply grid cells by to get time allocation with
        NROWS and NCOLS where the local time is converted based on the
        longitude
    """
    temporal = pd.read_csv(path)
    tkeys = ['hour%d' % i for i in range(1, 25)]
    tfrac = temporal.filter(tkeys).iloc[0].values
    tfrac /= tfrac.sum()
    start = tfrac[0]
    end = tfrac[-1]
    tfrac = np.append(tfrac, start)
    tfrac = np.append(end, tfrac)
    xcenters = np.arange(tfrac.size)
    xedges = xcenters[:-1] + 0.5
    tfactor = np.interp(xedges, xcenters, tfrac)

    i = np.arange(gf.NCOLS)
    j = np.arange(gf.NROWS)
    I, J = np.meshgrid(i, j)

    lon, lat = gf.ij2ll(I, J)
    tzoffs = (lon / 15).round(0).astype('i')[None, :, :]

    tfactors = {}
    for tzoff in np.unique(tzoffs):
        tfactors[tzoff] = np.roll(tfactor, -tzoff)

    tfactorarr = lon * np.zeros(25)[:, None, None, None]
    for idx, val in np.ndenumerate(tzoffs):
        tfactorarr[(slice(None),) + idx] = tfactors[val]
    return tfactorarr


def getspeciate(path):
    """
    Arguments
    ---------
    path : str
        Path to definitions of species translation.

    Returns
    -------
    evalexpr : str
        Just the contents of path.
    """
    evalexpr = open(path, mode='r').read()
    return evalexpr


def daily2hourly3d(
    inpath, outtmp, tpropath, layerpath, exprpath, dates=None, verbose=0
):
    """
    Convert daily 2d file to hourly 3d files
        - takes daily slices from inpath
        - allocates to 25 instantaneous hours
        - allocates to nl vertical layers.
        - converts speciation according to exprpath

    Arguments
    ---------
    inpath : str
        Path to daily IOAPI-like file
    outtmp : str
        strftime formatted template for hourly output (e.g., FINN_v1.5_%Y-%m-%d.nc)
    tpropath : str
        Temporal factor file (must be readable by gettemporal)
    layerpath : str
        Layer fraction file (must be readable by getvertical)
    exprpath : str
        Must have output definitions
    dates : None or list
        If a list, it should be a subset of dates to process
    verbose : int
        Level of verbosity
    
    Returns
    -------
    outf : NetCDF-like file
        PseudoNetCDF if OUTPATH is None; NetCDF otherwise.
    """

    if dates is None:
        dates = []
    print('Preparing inputs and factors', flush=True)
    inf = pnc.pncopen(inpath, format='ioapi')

    tfactor = gettemporal(tpropath, inf)
    vglvls, lfactor = getvertical(layerpath)
    evalexpr = getspeciate(exprpath)

    spcf = inf.copy().eval(evalexpr)
    # tfactor [=] e_{h} / e_{d}
    # lfactor [=] e_{x,z} / e_{x}
    # 1 / 3600 [=] e_{second} / e_{hour}
    # factor [=] e_{second,x,z} / e_{day,x}
    factor = tfactor[:] * lfactor[None, :, None, None] / 3600

    print('Preparing outputs', flush=True)
    outf = spcf.copy(dimensions=True, props=True, variables=False, data=False)
    # in_nt = len(spcf.dimensions['TSTEP'])
    out_nt = 24 + 1
    nz = lfactor.size

    outf.createDimension('TSTEP', out_nt)
    outf.createDimension('LAY', nz)

    # not applying factor to AREA or TFLAG.
    outkeys = [key for key in spcf.variables if key not in ('TFLAG', 'AREA')]
    for key in outkeys:
        inv = spcf.variables[key]
        outv = outf.copyVariable(inv, key=key, withdata=False)
        outv.units = inv.units.replace('/day', '/s').ljust(16)

    times = spcf.getTimes()
    print('Processing days', flush=True)
    gc.collect()
    for ti, time in enumerate(times):
        if len(args.dates) > 0:
            if time.strftime('%Y-%m-%d') not in args.dates:
                if args.verbose > 0:
                    print(time.strftime('Skipping %Y-%m-%d'), flush=True)
                continue
        outpath = time.strftime(args.outtmp)
        outdir = os.path.dirname(outpath)
        os.makedirs(outdir, exist_ok=True)
        if os.path.exists(outpath):
            print('Keeping', outpath, flush=True)
            continue
        print('Processing ' + time.strftime('%F'), end='.', flush=True)
        for key in outkeys:
            print(key, end='.', flush=True)
            inv = spcf.variables[key]
            outv = outf.variables[key]
            outv[:] = inv[ti] * factor

        del outf.variables['TFLAG']
        if 'nv' in outf.dimensions:
            del outf.dimensions['nv']
        if 'tnv' in outf.dimensions:
            del outf.dimensions['tnv']
        if hasattr(outf, 'Conventions'):
            delattr(outf, 'Conventions')
        if hasattr(outf, 'VAR-LIST'):
            delattr(outf, 'VAR-LIST')
        outf.SDATE = int(time.strftime('%Y%j'))
        outf.TSTEP = 10000
        outf.updatemeta()
        outf.variables.move_to_end('TFLAG', last=False)
        outf.UPNAM = "daily2hourly3d".ljust(16)
        outf.VGLVLS = vglvls
        history = (
            inf.HISTORY.strip()
            + "; Converted to hourly 3D IOAPI-like file from "
            + f"{args.inpath} using daily2hourly3d.py (v{__version__})"
        ).ljust(60*80)[:60*80]
        filedesc = (
            "FINN emissions as 3d hourly files with species and units"
            + " converted for use with CMAQ."
        ).ljust(60*80)[:60*80]
        outf.FILEDESC = filedesc
        outf.HISTORY = history

        print('Saving', flush=True)
        outf.save(
            outpath,
            format='NETCDF4_CLASSIC', complevel=1, verbose=0
        )
        gc.collect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument(
        '-l', '--layerpath', default='aux/layerfrac.csv',
        help='Layer fraction file'
    )
    parser.add_argument(
        '-t', '--tpropath', default='aux/tpro.txt',
        help='Hourly temporal profile path'
    )
    parser.add_argument(
        '-e', '--exprpath', default='aux/gc12_to_cb6r3_ae7.txt',
        help='Speciation conversion script path'
    )
    parser.add_argument(
        '-d', '--date', default=[], dest='dates', action='append',
        help='Process only this date YYYY-MM-DD (use multiple times)'
    )
    parser.add_argument('inpath')
    parser.add_argument('outtmp')
    args = parser.parse_args()
    outf = daily2hourly3d(**vars(args))
