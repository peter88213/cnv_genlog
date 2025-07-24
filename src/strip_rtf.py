#!/usr/bin/env python
"""Converts RTF into plain text.

Usage: strip_rtf.py path-to-rtf-file

Creates a utf-8 encoded text file 
with the same file name, but .txt extension.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/cnv_genlog
Published under the MIT License 
(https://opensource.org/licenses/mit-license.php)
"""

import os
import sys

from striprtf.striprtf import rtf_to_text


def main(rtf_file):
    with open(rtf_file, 'r', encoding='utf-8') as w:
        in_rtf = w.read()
    content = rtf_to_text(in_rtf)
    root, extension = os.path.splitext(rtf_file)
    with open(f'{root}.txt', 'w', encoding='utf-8') as w:
        w.write(content)


if __name__ == "__main__":
    main(sys.argv[1])
