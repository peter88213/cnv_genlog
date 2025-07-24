#!/usr/bin/env python
"""Parses a text file extracted and converted from a genlog HLP file.

Usage: parse-family_data.py path-to-txt-file

The kind of output file is still to be defined.
For the time being, the records are written to stdout.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/cnv_genlog
Published under the MIT License 
(https://opensource.org/licenses/mit-license.php)
"""
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


class Person:

    def __init__(self):
        self.name = None
        self.desc = []
        self.children = []
        self.father = None
        self.mother = None
        self.birth = None
        self.death = None
        self.documents = []
        self.spouses = []
        self.image = None


def print_people(people):
    for i, personId in enumerate(people):
        person = people[personId]
        print('-' * 60)
        print(f'ID  :     {personId}')
        print('-' * 60)
        print(f'Name:     {person.name}')
        print(f'Image:    {person.image}')
        print(f'Born:     {person.birth}')
        print(f'Died:     {person.death}')
        print(f'Father:   {person.father}')
        print(f'Mother:   {person.mother}')
        for spouse in person.spouses:
            print(f'Spouse:   {spouse}')
        for child in person.children:
            print(f'Child:    {child}')
        for document in person.documents:
            print(f'Document: {document}')
        print()
        for desc in person.desc:
            if desc:
                print(f'          {desc}')
        print()
    print(f'{i} records found.')


def add_person(people, person, key):
    if key:
        people[key] = person


def change_state(state, new_state, person, text):
    if state == EXPECT_NAME:
        if text:
            person.name = text.strip()
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
            state = state = change_state(state, EXPECT_DESC, person, line)
            text.clear()
        elif not line and state != EXPECT_NAME:
            state = state = change_state(state, EXPECT_DESC, person, '\n'.join(text))
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


if __name__ == "__main__":
    main(sys.argv[1])
