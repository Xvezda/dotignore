#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Xvezda <xvezda@naver.com>
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from .core import git_command


def main():
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    import textwrap
    git_epilog = textwrap.dedent('''\
    trouble shooting:
        Q. Error `response code from api server is not ok`
        A. API quota is exhausted.
           Set `GITHUB_API_TOKEN` environment variable or `--token` option to authorize,
           or try later for unauthorized use cases.
    ''')
    git_parser = subparsers.add_parser(
        'git',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=git_epilog
    )
    git_parser.add_argument('--list', '-l', action='store_true',
                            help='show list of language names')
    git_parser.add_argument('--output', '-o', type=str, default='.gitignore',
                            help='set output name of file '
                                 '(default: %(default)s)')
    git_parser.add_argument('--append', '-a', action='store_true',
                            help='append to .gitignore file if already exists')
    git_parser.add_argument('--token', '-t', type=str, default='',
                            help='set GitHub api token')
    git_parser.add_argument('name', nargs='?')
    git_parser.set_defaults(func=git_command)

    args = parser.parse_args()

    try:
        args.func(args)
    except AttributeError:
        parser.print_help()


if __name__ == '__main__':
    main()

