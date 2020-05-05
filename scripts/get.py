#!/usr/bin/env python
import argparse
from datetime import datetime
from urllib.request import urlretrieve
import os

URLTMPL= (
    'https://www.acom.ucar.edu/acresp/MODELING/finn_emis_txt/' +
    'GLOB_GEOSchem_%Y%j.txt.gz'
)

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--format', default='%Y-%m-%d', metavar='STRFTIME')
parser.add_argument('dates', metavar='YYYY-MM-DD', nargs='+')
args = parser.parse_args()

for datestr in args.dates:
    date = datetime.strptime(datestr, args.format)
    url = date.strftime(URLTMPL)
    target = url.replace('https://', '')
    outdir = os.path.dirname(target)
    os.makedirs(outdir, exist_ok=True)
    if os.path.exists(target):
        print('Keeping cached', target)
    else:
        print('Downloading', target)
        urlretrieve(url, target)

