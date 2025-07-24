#!/usr/bin/env python
"""Parses a text file extracted and converted from a genlog HLP file.

Usage: parse-family_data.py path-to-txt-file

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/cnv_genlog
Published under the MIT License 
(https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
import re

RECORD_MARKER = '$#K'
IMAGE_MARKER = '{bmc '
NO_DATE = 'o.D.'
LINK_MARKER = '>main'
image_pattern = re.compile(r'{bmc (.*?)\.BMP}')

# Parser states.
EXPECT_NAME = 0
EXPECT_DESC = 1
EXPECT_FATHER = 2
EXPECT_MOTHER = 3
EXPECT_CHILDREN = 4
EXPECT_PROFESSION = 5


class Person:

    def __init__(self):
        self.name = None
        self.profession = None
        self.desc = []
        self.children = []
        self.father = None
        self.mother = None
        self.birth = None
        self.death = None
        self.documents = []
        self.spouses = []
        self.image = None


def serialize_people(people):
    lines = []
    for i, personId in enumerate(people):
        person = people[personId]
        lines.append('-' * 60)
        lines.append(f'ID  :        {personId}')
        lines.append('-' * 60)
        lines.append(f'Name:        {person.name}')
        if person.profession:
            lines.append(f'Beruf:       {person.profession}')
        if person.image:
            lines.append(f'Bild:        {person.image}')
        if person.birth:
            lines.append(f'Geboren:     {person.birth}')
        if person.death:
            lines.append(f'Gestorben:   {person.death}')
        if person.father:
            lines.append(f'Vater:       {person.father}')
        if person.mother:
            lines.append(f'Mutter:      {person.mother}')
        for spouse in person.spouses:
            lines.append(f'Verheiratet: {spouse}')
        for child in person.children:
            lines.append(f'Kind:        {child}')
        for document in person.documents:
            lines.append(f'Dokument:    {document}')
        lines.append('')
        for desc in person.desc:
            if desc:
                lines.append(desc)
        lines.append('')
    lines.append(f'{i} Datensätze gefunden')
    return lines


def print_people(people):
    lines = serialize_people(people)
    for line in lines:
        print(line)


def write_people(file_path, people):
    lines = serialize_people(people)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def add_person(people, person, key):
    if key:
        people[key] = person


def leave_state(state, person, text):
    if state == EXPECT_NAME:
        if text:
            person.name = text.strip()
    elif state == EXPECT_PROFESSION:
        if text:
            person.profession = text.strip()
    elif state == EXPECT_DESC:
        if text:
            text = text.strip()
            if text:
                person.desc.append(text)
    elif state == EXPECT_FATHER:
        if text:
            person.father = text.strip()
    elif state == EXPECT_MOTHER:
        if text:
            person.mother = text.strip()
    elif state == EXPECT_CHILDREN:
        if text:
            person.children = text.split('\n')


def parse_lines(lines):
    state = None
    people = {}
    text = []
    key = None
    person = None
    image = None
    for line in lines:
        if line.startswith(RECORD_MARKER):
            add_person(people, person, key)
            person = Person()
            key = line[len(RECORD_MARKER):].strip()
            leave_state(state, person, '')
            state = EXPECT_NAME
        elif line.startswith(IMAGE_MARKER):
            image = image_pattern.search(line).group(1)
            if image:
                person.image = image
        elif line.startswith('oo'):
            leave_state(state, person, '\n'.join(text))
            state = EXPECT_DESC
            text.clear()
            person.spouses.append(line[2:].strip())
        elif line.startswith('*'):
            leave_state(state, person, '\n'.join(text))
            state = EXPECT_DESC
            text.clear()
            person.birth = line[1:].strip()
        elif line.startswith('+'):
            leave_state(state, person, '\n'.join(text))
            state = EXPECT_DESC
            text.clear()
            person.death = line[1:].strip()
        elif line.startswith('Vater:'):
            leave_state(state, person, '\n'.join(text))
            state = EXPECT_FATHER
            text.clear()
        elif line.startswith('Mutter:'):
            leave_state(state, person, '\n'.join(text))
            state = EXPECT_MOTHER
            text.clear()
        elif line.startswith('Kinder:'):
            leave_state(state, person, '\n'.join(text))
            state = EXPECT_CHILDREN
            text.clear()
        elif line and state == EXPECT_NAME:
            leave_state(state, person, line)
            state = EXPECT_PROFESSION
            text.clear()
        elif line and state == EXPECT_PROFESSION:
            leave_state(state, person, line)
            state = EXPECT_DESC
            text.clear()
        elif not line and state != EXPECT_NAME:
            leave_state(state, person, '\n'.join(text))
            state = EXPECT_DESC
            text.clear()
        else:
            text.append(line)
    add_person(people, person, key)
    return people


def main(file_path):
    with open(file_path, 'r', encoding='utf-8') as w:
        lines = w.read().split('\n')
    people = parse_lines(lines)
    # print_people(people)
    # return

    root, extension = os.path.splitext(file_path)
    result_file = f'{root}_parsed.txt'
    write_people(result_file, people)


if __name__ == "__main__":
    main(sys.argv[1])
