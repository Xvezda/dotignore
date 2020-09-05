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

import re
import os
import sys
import json
import logging
import requests

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


GITHUB_API_URL = 'https://api.github.com/gitignore/templates'


def soundex(text):
    """
    [Soundex on Wikipedia](https://en.wikipedia.org/wiki/Soundex)

    > The correct value can be found as follows:
    >
    > 1. Retain the first letter of the name and drop all other occurrences of
    >    a, e, i, o, u, y, h, w.
    > 2. Replace consonants with digits as follows (after the first letter):
    >    b, f, p, v → 1
    >    c, g, j, k, q, s, x, z → 2
    >    d, t → 3
    >    l → 4
    >    m, n → 5
    >    r → 6
    > 3. If two or more letters with the same number are adjacent in the original name
    >    (before step 1), only retain the first letter;
    >    also two letters with the same number separated by 'h' or 'w' are coded as a single number,
    >    whereas such letters separated by a vowel are coded twice.
    >    This rule also applies to the first letter.
    > 4. If you have too few letters in your word that you can't assign three numbers,
    >    append with zeros until there are three numbers.
    >    If you have four or more numbers, retain only the first three.
    """
    # Step 1
    first_letter = text[:1]

    occurrences = ['a', 'e', 'i', 'o', 'u', 'y']  # `h` and `w` will be ignored
    remain_text = text[1:].lower()

    for occurrence in occurrences:
        remain_text = remain_text.replace(occurrence, '0')
    logger.info('Step 1: %s' % remain_text)

    # Step 2
    mapping = [
        None,
        ['b', 'f', 'p', 'v'],                     # 1
        ['c', 'g', 'j', 'k', 'q', 's', 'x', 'z'], # 2
        ['d', 't'],                               # 3
        ['l'],                                    # 4
        ['m', 'n'],                               # 5
        ['r']                                     # 6
    ]

    def number_of(letter):
        for idx, seq in enumerate(mapping):
            if not seq:
                continue
            if letter.lower() in seq:
                return str(idx)
        return letter

    mapped = remain_text
    for letter in remain_text:
        mapped = mapped.replace(letter, number_of(letter))
    logger.info('Step 2: %s' % mapped)

    # Step 3
    first_letter_number = number_of(first_letter)
    mapped = first_letter_number + mapped

    mapped = re.sub(r'([1-6])\1+', r'\1', mapped)
    logger.info('Step 3-1: %s' % mapped)

    mapped = re.sub(r'([1-6])[hw]\1', r'\1', mapped)
    logger.info('Step 3-2: %s' % mapped)

    # Remove prepended first letter
    mapped = re.sub(r'^%s' % first_letter_number, '', mapped)
    # Remove occurrences
    mapped = re.sub('[hw]', '', mapped)
    mapped = mapped.replace('0', '')

    result = first_letter + mapped[:3].ljust(3, '0')
    return result.upper()


def distance(a, b):
    """Get levenshtein distance"""

    def _matrix(a, b):
        """Generate matrix of levenshtein distance"""
        matrix = []
        matrix.append(range(len(b)+1))
        for i in range(1, len(a)+1):
            matrix.append([i] + [None]*len(b))

        for j, y in enumerate(list(a)):
            for i, x in enumerate(list(b)):
                if x == y:
                    matrix[j+1][i+1] = matrix[j][i]
                else:
                    matrix[j+1][i+1] = 1 + min(
                        matrix[j][i],
                        matrix[j][i+1],
                        matrix[j+1][i]
                    )
        return matrix

    matrix = _matrix(a, b)
    return matrix[-1][-1]


def rank(haystack, needle):
    new_haystack = []
    for hay in haystack:
        # Get levenshtein distance
        new_haystack.append((hay, distance(hay.lower(), needle.lower())))

    for idx, hay in enumerate(new_haystack):
        # Additional calculation using soundex
        key, dist = hay
        dist += distance(soundex(key), soundex(needle))
        new_haystack[idx] = (key, dist)

    for idx, hay in enumerate(new_haystack):
        key, dist = hay
        # Heuristic approach
        # Give higher priority if target contains keyword
        if key.lower().startswith(needle.lower()):
            dist -= 7
        elif needle.lower() in key.lower():
            dist -= 3
        new_haystack[idx] = (key, dist)

    return sorted(new_haystack, key=lambda x: x[1])


def exit_api_error():
    print('response code from api server is not ok', end='\n\n',
          file=sys.stderr)
    print('see `%s git --help` for more help' % sys.argv[0],
          file=sys.stderr)
    sys.exit(1)


def git_command(args):
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }

    token = os.getenv('GITHUB_API_TOKEN', args.token)
    if token:
        headers['Authorization'] = 'token %s' % token

    r = requests.get(GITHUB_API_URL, headers=headers)
    if r.status_code != 200:
        return exit_api_error()

    langs = json.loads(r.text)

    if args.list:
        print('\n'.join(langs))
        return

    if args.name:
        closest = rank(langs, args.name)[0]
        name, dist = closest

        r = requests.get(GITHUB_API_URL + '/%s' % name)
        if r.status_code != 200:
            return exit_api_error()

        res = json.loads(r.text)
        source = res.get('source')
        mode = 'w'
        if os.path.exists(args.output):
            if not args.append:
                print("file '%s' already exists!" % args.output,
                      file=sys.stderr)
                return sys.exit(1)
            mode = 'a'

        with open(args.output, mode) as f:
            f.write(source)
        print('template of %s has been used' % name)

