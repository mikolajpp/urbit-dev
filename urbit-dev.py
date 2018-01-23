#!/usr/bin/env python
"""Urbit Developer Tool.

Usage:
  urbit-dev (link|clean) [-ud] [--arvo=<arvo_dir>]... <src> <desk>

Options:
  -h --help              Show this screen.
  --version              Show version.
  -a --arvo=<arvo_dir>   Scan only given arvo dir.
  -d --debug             Debug printing.
  -u --unsafe            Link even large files (> 10MB).
"""
from docopt import docopt
from pathlib import Path


# General settings
arvo_skel = [ '/app',
                '/gen',
                '/lib',
                '/mar',
                '/ren',
                '/sec',
                '/sur',
                '/sys',
                '/web']

# Do not link files exceeding mem_limit(MB)
mem_limit = 10*1024**2


def scan_src(path, link_targets, debug = False):

    for f in path.iterdir():
        if f.is_file():
            if debug:
                print("+ Found {}, size = {}".format(f, f.stat().st_size))
            if f.stat().st_size > mem_limit:
                print("{} size exceeded {}, skipping".format(f, mem_limit))
            else:
                link_targets.append(f)

        elif f.is_dir():
            if debug:
                print("Recursing into {}/".format(f))
            link_targets.extend(scan_src(f, [], debug))

    return link_targets

def link_to(src, target, desk):
    symlink = desk / target.relative_to(src)
    print("Linking {} -> {}".format(symlink, target.resolve()))

    try:
        symlink.symlink_to(target.resolve())

    except FileNotFoundError:
        symlink.parent.mkdir(parents=True)
        symlink.symlink_to(target.resolve())
    except FileExistsError:
        print("File exists, please fix your structure")


def link(src, desk, debug = False):

    link_targets = []

    for arv in arvo_skel:
        try:
            src_path = Path(src + arv)

            if src_path.exists:
                if debug:
                    print("Scanning {}/".format(src_path))
                link_targets.extend(scan_src(src_path, [], debug))

        except FileNotFoundError:
            if debug:
                print("Arvo directory {}/ not found, skip".format(arv))
            continue

        except PermissionError:
            print("No permission to access {}, skip".format(arv))

        except:
            print("Failed to scan {}".format(arv))

    for tar in link_targets:
        link_to(src, tar, Path(desk))


if __name__ == '__main__':
    args = docopt(__doc__, version="Urbit Developer Tool 0.1.0")

    if args['link']:
        link(args['<src>'], args['<desk>'], args['--debug'])
