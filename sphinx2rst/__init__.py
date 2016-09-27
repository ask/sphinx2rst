#/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import codecs
import os
import re
import sys

from collections import Callable
from functools import partial

SAY = partial(print, file=sys.stderr)

dirname = ['']

RE_CODE_BLOCK = re.compile(r'(\s*).. code-block:: (.+?)\s*$')
RE_INCLUDE = re.compile(r'\s*.. include:: (.+?)\s*$')
RE_REFERENCE = re.compile(r':(\w+):`(.+?)`')
RE_NAMED_REF = re.compile('(.+?)\<(.+)\>')
RE_SETTING = re.compile(r'.. setting::')
UNITABLE = {
    '…': '...',
    '“': '"',
    '”': '"',
}
X = re.compile(re.escape('…'))
HEADER = re.compile('^[\=\~\-]+$')
UNIRE = re.compile('|'.join(re.escape(p) for p in UNITABLE),
                   re.UNICODE)

CONFIGPATH = os.environ.get('SPHINX2RSTCONFIG') or os.path.join(
    'extra', 'release',
)
sys.path.append(CONFIGPATH)

try:
    from sphinx2rst_config import REFBASE, REFS
except ImportError:
    REFBASE = ''  # noqa
    REFS = ''     # noqa


pending_refs = {}


def _replace_handler(match, key=UNITABLE.__getitem__):
    return key(match.group(0))


def include_file(lines, pos, match):
    orig_filename = match.groups()[0]
    filename = os.path.join(dirname[0], orig_filename)
    fh = codecs.open(filename, encoding='utf-8')
    try:
        old_dirname = dirname[0]
        dirname[0] = os.path.dirname(orig_filename)
        try:
            lines[pos] = sphinx_to_rst(fh)
        finally:
            dirname[0] = old_dirname
    finally:
        fh.close()


def asciify(lines):
    prev_diff = None
    for line in lines:
        new_line = UNIRE.sub(_replace_handler, line)
        if prev_diff and HEADER.match(new_line):
            new_line = ''.join([
                new_line.rstrip(), new_line[0] * prev_diff, '\n'])
        prev_diff = len(new_line) - len(line)
        yield new_line.encode('ascii').decode()


def replace_code_block(lines, pos, match):
    lines[pos] = ''
    curpos = pos - 1
    # Find the first previous line with text to append "::" to it.
    while True:
        prev_line = lines[curpos]
        if not prev_line.isspace():
            prev_line_with_text = curpos
            break
        curpos -= 1

    if lines[prev_line_with_text].endswith(':'):
        lines[prev_line_with_text] += ':'
    else:
        lines[prev_line_with_text] += '\n' + match.group(1) + '::'


def remove_line(lines, i, match):
    lines[i] = ''


def _deref_default(target):
    return r'``{0}``'.format(target)


def _deref_ref(target):
    m = RE_NAMED_REF.match(target)
    if m:
        text, target = m.group(1).strip(), m.group(2).strip()
    else:
        text = target

    try:
        url = REFS[target]
    except KeyError:
        return _deref_default(target)

    if '://' not in url:
        url = '/'.join([REFBASE, url])
    pending_refs[text] = url

    return r'`{0}`_'.format(text)


DEREF = {'ref': _deref_ref}


def _deref(match):
    return DEREF.get(match.group(1), _deref_default)(match.group(2))


def deref_all(line):
    return RE_REFERENCE.subn(_deref, line)[0]


def resolve_ref(name, url):
    return '\n.. _`{0}`: {1}\n'.format(name, url)


def resolve_pending_refs(lines):
    for line in lines:
        yield line
    for name, url in pending_refs.items():
        yield resolve_ref(name, url)


TO_RST_MAP = {
    RE_CODE_BLOCK: replace_code_block,
    RE_INCLUDE: include_file,
    RE_SETTING: remove_line,
}


def _process(lines, encoding='utf-8'):
    lines = list(lines)                                 # non-destructive
    for i, line in enumerate(lines):
        for regex, alt in TO_RST_MAP.items():
            if isinstance(alt, Callable):
                match = regex.match(line)
                if match:
                    alt(lines, i, match)
                    line = lines[i]
            else:
                lines[i] = regex.sub(alt, line)
        lines[i] = deref_all(lines[i])
    if encoding == 'ascii':
        lines = asciify(lines)
    return resolve_pending_refs(lines)


def sphinx_to_rst(fh, encoding='utf-8'):
    return ''.join(_process(fh, encoding))


def main(argv=sys.argv):
    if len(sys.argv) < 2:
        raise Exception('Missing filename')
    dirname[0] = os.path.dirname(sys.argv[1])
    encoding = 'ascii' if '--ascii' in sys.argv else 'utf-8'
    with codecs.open(sys.argv[1], encoding='utf-8') as fh:
        print(sphinx_to_rst(fh, encoding).encode('utf-8').decode())


if __name__ == '__main__':
    main()
