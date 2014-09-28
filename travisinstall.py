#!/usr/bin/env python
"""
Custom install command for PySide when using travis ci.
"""
from __future__ import print_function

import sys
import subprocess


def start_process(args):
    p = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    print(p.communicate())
    rc = p.poll()
    if rc:
        print('Pip install returncode: %s for args %s' % (rc, args), file=sys.stderr)
        sys.exit(rc)

args = ['pip', 'install', 'PySide', '--no-index', '--find-links', 'https://parkin.github.io/python-wheelhouse/']
start_process(args)

args = ['pip', 'install', '--pre']
args.extend(sys.argv[1:])
start_process(args)
