#!/usr/bin/env python3

import os, sys
import re
from itertools import chain
import re
import json
from collections import Counter
import hashlib
import argparse

from keywords import KEYWORDS


def strhash(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()


def simplify_spaces(s):
    return re.sub('\s+', ' ', s)


def strip_comments(text):
    return re.sub('//.*?\n|/\*.*?\*/', '', text, flags=re.S)


def is_numeric(s):
    try:
        float(s)
        return True
    except:
        return False


SCANNER = re.Scanner([
    (r"[a-zA-Z_\$][a-zA-Z_0-9\$]*", lambda scanner, token: ("ID",  token)),
    (r"\s+",                        lambda scanner, token: ('SP',  ' ')),
    (r"\"\"\"[^$\"\"\"]+\"\"\"",    lambda scanner, token: ('STR', "")),
    (r"\"[^$\"]+\"",                lambda scanner, token: ('STR', "")),
    (r".",                          lambda scanner, token: ('O',   token)),
])


def find_all(basedir, pred):
    for root, dirs, files in os.walk(basedir):
        for fn in files:
            path = os.path.join(root, fn)
            if pred(path):
                yield path


BANNED_SNIPPETS = set([
    '====================',
    'scala.reflect.macros',
    'experimental.macros',
    'reflect.macros.Context',
    'GenTraversable',
    'GenTraversableOnce',
    '@deprecated',
    'convert.ImplicitConversionsToScala',
    'java.',
    'scala.collection',
    'dotty.tools.dotc',
    '.runtime.universe',
    'math.ScalaNumber',
    '.concurrent.Future',
    '.api.JavaUniverse',
    'concurrent.ExecutionContext',
    'tools.nsc',
    'scala.reflect.io'])


def is_valid_source(source):
    has_unicode = (any(ord(ch) > 127 for ch in source)
                   or re.match(r'\\u[a-fA-F0-9]{4}', source) is not None)
    has_banned_snippets = any(x in source for x in BANNED_SNIPPETS)
    return not has_unicode and not has_banned_snippets


def strip_source(source):
    source = (line.strip() for line in source.split('\n'))
    source = (simplify_spaces(line).strip() for line in source)
    source = (line for line in source if line != '' or line.startswith('//'))
    source = strip_comments('\n'.join(source))
    return source


def main():
    args = parse_args()

    dottytests = os.path.join(args.dottydir, 'tests')
    scalatests = os.path.join(args.scaladir, 'tests')

    files = chain(
        find_all(dottytests, lambda p: p.endswith('.scala')),
        find_all(scalatests, lambda p: p.endswith('.scala')))

    sources = []
    for fn in files:
        base, ext = os.path.splitext(fn)
        flags_fn = base + '.flags'

        with open(fn, 'rt') as fin:
            try:
                source = fin.read()
            except:
                print("Could not read %s" % fn)

        if os.path.isfile(flags_fn):
            with open(flags_fn, 'rt') as fin:
                try:
                    flags = fin.read().strip()
                except:
                    print("Could not read %s" % fn)
        else:
            flags = None

        source = strip_source(source)
        if not is_valid_source(source):
            continue
        sources.append((flags, source))

    frequency = Counter()
    for _, source in sources:
        results, remainder = SCANNER.scan(source)
        for k, r in results:
            if k == 'ID':
                frequency.update([r])

    ordered_voc = {w: i for i, (w, c) in enumerate(frequency.most_common())}

    voc = ((w, ordered_voc[w]) for i, w in enumerate(KEYWORDS)
           if w in ordered_voc)
    voc = sorted(voc, key=lambda t: t[-1])
    voc = dict((w, 'k' + str(i)) for i, (w, _) in enumerate(voc))

    rvoc = dict((w, k) for k, w in voc.items())

    print("Generated vocabulary.")
    with open('rvoc.json', 'wt+') as fout:
        print(json.dumps(rvoc), file=fout)

    processed_sources = []
    hashes = set()
    for _, source in sources:
        parts = []
        ids = {}
        for line in source.split('\n'):
            if '//' in line:
                line = line[:line.find('//')]
            results, remainder = SCANNER.scan(line)
            assert(remainder == '')

            line_parts = []
            for k, r in results:
                if r in voc:
                    line_parts.append(voc[r])
                elif k == 'ID':
                    if r not in ids:
                        if r[0].islower():
                            ids[r] = 'i%d' % len(ids)
                        else:
                            ids[r] = 'I%d' % len(ids)
                    line_parts.append(ids[r])
                else:
                    line_parts.append(r)
            line_parts = ''.join(line_parts)
            line_parts = line_parts.strip()
            if line_parts == '':
                continue
            parts.append(''.join(line_parts))
        source = '\n'.join(parts)
        source = source.strip()
        if source == '':
            continue
        source_hash = strhash(source)
        if source_hash in hashes:
            continue
        hashes.add(source_hash)
        processed_sources.append(source)

    with open('sources.txt', 'wt+') as fout:
        print('\n\1\n'.join(processed_sources), file=fout)


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('dottydir', type=str)
    argparser.add_argument('scaladir', type=str)
    return argparser.parse_args()


if __name__ == "__main__":
    main()
