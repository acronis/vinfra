#!/usr/bin/env python

import os
import argparse

GET = 'get'
INC = 'inc'

makefile_version = os.path.join(__file__, '..', '..', 'Makefile.version')
makefile_version = os.path.abspath(makefile_version)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--action',
        choices=[GET, INC],
        help="Action %s or %s" % (GET, INC)
    )
    parsed = parser.parse_args()
    return parsed


def get_version():
    return open(makefile_version).read().rstrip("\n")


def inc_version():
    ver = [int(v) for v in get_version().split('.')]
    ver[-1] += 1
    ver_str = '.'.join(map(str, ver))
    open(makefile_version, 'w').write(ver_str)
    return ver_str


if __name__ == '__main__':
    parsed = parse_args()
    ver = {
        GET: get_version,
        INC: inc_version,
    }[parsed.action]()
    print(ver)
