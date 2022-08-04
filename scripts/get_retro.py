#!/usr/bin/env python
import argparse
from datetime import datetime
from urllib.request import urlretrieve
import os

URLTMPL = (
    'http://www.acom.ucar.edu/Data/fire/data/finn1/FINNv1.5_%Y.GEOSCHEM.tar.gz'
)

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--format', default='%Y-%m-%d', metavar='STRFTIME')
parser.add_argument('date', metavar='YYYY-MM-DD')
args = parser.parse_args()

for datestr in [args.date]:
    date = datetime.strptime(datestr, args.format)
    url = date.strftime(URLTMPL)
    target = url.replace('http://', '')
    outdir = os.path.dirname(target)
    os.makedirs(outdir, exist_ok=True)
    if os.path.exists(target):
        print('Keeping cached', target)
    else:
        print('Downloading', target)
        urlretrieve(url, target)
