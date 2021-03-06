#!/usr/bin/env python
import numpy as np
import pandas as pd
import PseudoNetCDF as pnc
import gc
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-l', '--layerpath', default='aux/layerfrac.csv')
parser.add_argument('-t', '--tpropath', default='aux/tpro.txt')
parser.add_argument('-e', '--exprpath', default='aux/gc12_to_cb6r3_ae7.txt')
parser.add_argument('inpath')
parser.add_argument('outtmp')
args = parser.parse_args()


def getvertical(path):
    layerfrac = pd.read_csv(path)
    return layerfrac['frac'].values


def gettemporal(path, gf):
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
    evalexpr = open(path, mode='r').read()
    return evalexpr


print('Preparing inputs and factors', flush=True)
inf = pnc.pncopen(args.inpath, format='ioapi')

tfactor = gettemporal(args.tpropath, inf)
lfactor = getvertical(args.layerpath)
evalexpr = getspeciate(args.exprpath)

spcf = inf.copy().eval(evalexpr)
factor = tfactor[:] * lfactor[None, :, None, None]

print('Preparing outputs', flush=True)
outf = spcf.copy(dimensions=True, props=True, variables=False, data=False)
in_nt = len(spcf.dimensions['TSTEP'])
out_nt = 24 + 1
nz = lfactor.size

outf.createDimension('TSTEP', out_nt)
outf.createDimension('LAY', nz)

outkeys = [key for key in spcf.variables if key != 'TFLAG']
for key in outkeys:
    inv = spcf.variables[key]
    outv = outf.copyVariable(inv, key=key, withdata=False)

times = spcf.getTimes()
print('Processing days', flush=True)
gc.collect()
for ti, time in enumerate(times):
    outpath = time.strftime(args.outtmp)
    outdir = os.path.dirname(outpath)
    os.makedirs(outdir, exist_ok=True)
    if os.path.exists(outpath):
        print('Keeping', outpath, flush=True)
        continue
    print('Processing ' + time.strftime('%F'), end='.', flush=True)
    for key in outkeys:
        print(key, end='.')
        inv = spcf.variables[key]
        outv = outf.variables[key]
        outv[:] = inv[ti] * factor

    del outf.variables['TFLAG']
    outf.SDATE = int(time.strftime('%Y%j'))
    outf.TSTEP = 10000
    outf.updatemeta()
    print('Saving', flush=True)
    outf.save(
        outpath,
        format='NETCDF4_CLASSIC', complevel=1, verbose=0
    )
    gc.collect()
