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
        lines.append(f'ID  :       {personId}')
        lines.append('-' * 60)
        lines.append(f'Name:       {person.name}')
        lines.append(f'Profession: {person.profession}')
        lines.append(f'Image:      {person.image}')
        lines.append(f'Born:       {person.birth}')
        lines.append(f'Died:       {person.death}')
        lines.append(f'Father:     {person.father}')
        lines.append(f'Mother:     {person.mother}')
        for spouse in person.spouses:
            lines.append(f'Spouse:     {spouse}')
        for child in person.children:
            lines.append(f'Child:      {child}')
        for document in person.documents:
            lines.append(f'Document:   {document}')
        lines.append('')
        for desc in person.desc:
            if desc:
                lines.append(f'            {desc}')
        lines.append('')
    lines.append(f'{i} records found.')
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


def change_state(state, new_state, person, text):
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
    return new_state


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
            state = change_state(state, EXPECT_NAME, person, '')
        elif line.startswith(IMAGE_MARKER):
            image = image_pattern.search(line).group(1)
            if image:
                person.image = image
        elif line.startswith('oo '):
            state = change_state(state, EXPECT_DESC, person, '\n'.join(text))
            text.clear()
            person.spouses.append(line[2:].strip())
        elif line.startswith('* '):
            state = change_state(state, EXPECT_DESC, person, '\n'.join(text))
            text.clear()
            person.birth = line[2:].strip()
        elif line.startswith('+ '):
            state = change_state(state, EXPECT_DESC, person, '\n'.join(text))
            text.clear()
            person.death = line[2:].strip()
        elif line.startswith('Vater:'):
            state = change_state(state, EXPECT_FATHER, person, '\n'.join(text))
            text.clear()
        elif line.startswith('Mutter:'):
            state = change_state(state, EXPECT_MOTHER, person, '\n'.join(text))
            text.clear()
        elif line.startswith('Kinder:'):
            state = change_state(state, EXPECT_CHILDREN, person, '\n'.join(text))
            text.clear()
        elif line and state == EXPECT_NAME:
            state = change_state(state, EXPECT_PROFESSION, person, line)
            text.clear()
        elif line and state == EXPECT_PROFESSION:
            state = change_state(state, EXPECT_DESC, person, line)
            text.clear()
        elif not line and state != EXPECT_NAME:
            state = change_state(state, EXPECT_DESC, person, '\n'.join(text))
            text.clear()
        else:
            text.append(line)
    add_person(people, person, key)
    return people


def main(file_path):
    with open(file_path, 'r', encoding='utf-8') as w:
        lines = w.read().split('\n')
    people = parse_lines(lines)
    print_people(people)
    return

    root, extension = os.path.splitext(file_path)
    result_file = f'{root}_parsed.txt'
    write_people(result_file, people)


if __name__ == "__main__":
    main(sys.argv[1])
