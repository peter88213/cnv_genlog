#!/usr/bin/env python
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
