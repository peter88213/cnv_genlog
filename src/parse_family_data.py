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
IMAGE_SUBDIR = 'images'

# Parser states.
EXPECT_NAME = 0
EXPECT_DESC = 1
EXPECT_FATHER = 2
EXPECT_MOTHER = 3
EXPECT_CHILDREN = 4
EXPECT_PROFESSION = 5
EXPECT_DOCUMENTS = 6


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

    def get_record(self, person_id=None):

        #--- YAML part.
        lines = ['---']
        if person_id:
            lines.append(f'ID: {person_id}')
        lines.append(f'Name: {self.name}')
        if self.profession:
            lines.append(f'Beruf: {self.profession}')
        if self.birth:
            lines.append(f'Geboren: {self.birth}')
        if self.death:
            lines.append(f'Gestorben: {self.death}')
        if self.father:
            lines.append(f'Vater: {self._sanitize_link(self.father)}')
        if self.mother:
            lines.append(f'Mutter: {self._sanitize_link(self.mother)}')
        if self.spouses:
            lines.append('Ehepartner:')
            for spouse in self.spouses:
                lines.append(f'  - {self._sanitize_link(spouse)}')
        if self.children:
            lines.append('Kinder:')
            for child in self.children:
                lines.append(f'  - {self._sanitize_link(child)}')
        if self.documents:
            lines.append('Dokumente:')
            for document in self.documents:
                lines.append(f'  - {self._sanitize_link(document)}')
        lines.append('---')

        #--- Markdown text part.

        if self.image:
            lines.append(f'![[{IMAGE_SUBDIR}/{self.image}|Bild]]')
            lines.append('')
        for desc in self.desc:
            if desc:
                lines.append(desc)

        if self.spouses:
            lines.append('### Verheiratet:')
            for spouse in self.spouses:
                lines.append(f'  - {spouse}')

        return lines

    def _sanitize_link(self, text):
        return re.sub(r'.*?\[\[(.*?)\]\].*', r'"[[\1]]"', text)

    def _unlink(self, text):
        return text.replace('[[', '').replace(']]', '')


def serialize_people(people):
    lines = []
    for i, person_id in enumerate(people):
        lines.extend(people[person_id].get_record(person_id))
        lines.append('')
    lines.append(f'{i} Datensätze gefunden')
    return lines


def print_people(people):
    lines = serialize_people(people)
    for line in lines:
        print(line)


def write_single_text_file(file_path, people):
    lines = serialize_people(people)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def sanitize_title(title):
    # Return title with disallowed characters removed.
    return re.sub(r'[\\|\/|\:|\*|\?|\"|\<|\>|\|]+', '', title)


def write_obsidian_notes(folder_path, people):
    os.makedirs(folder_path, exist_ok=True)

    for person_id in people:
        title = sanitize_title(person_id)
        lines = people[person_id].get_record()
        with open(f'{folder_path}/{title}.md', 'w', encoding='utf-8') as f:
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
    elif state == EXPECT_DOCUMENTS:
        if text:
            person.documents = text.split('\n')


def parse_lines(lines, personClass=Person):
    state = None
    people = {}
    text = []
    key = None
    person = None
    image = None
    for line in lines:
        if line.startswith(RECORD_MARKER):
            add_person(people, person, key)
            person = personClass()
            key = line[len(RECORD_MARKER):].strip()
            leave_state(state, person, '')
            state = EXPECT_NAME
        elif line.startswith(IMAGE_MARKER):
            image = image_pattern.search(line).group(1)
            if image:
                person.image = f'{image}.jpg'
        elif line.startswith('oo'):
            leave_state(state, person, '\n'.join(text))
            state = EXPECT_DESC
            text.clear()
            person.spouses.append(line[2:].strip())
        elif line.startswith('*') and not person.birth:
            leave_state(state, person, '\n'.join(text))
            state = EXPECT_DESC
            text.clear()
            person.birth = line[1:].strip()
        elif line.startswith('+') and not person.death:
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
        elif line.startswith('Dokumente:'):
            leave_state(state, person, '\n'.join(text))
            state = EXPECT_DOCUMENTS
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


# Output variants.
SCREEN = 0
TEXT_FILE = 1
OBSIDIAN_NOTES = 2


def main(file_path, output=SCREEN):
    root, extension = os.path.splitext(file_path)
    with open(file_path, 'r', encoding='utf-8') as w:
        lines = w.read().split('\n')
    people = parse_lines(lines)
    if output == SCREEN:
        print_people(people)
    elif output == TEXT_FILE:
        result_file = f'{root}_parsed.txt'
        write_single_text_file(result_file, people)
    elif output == OBSIDIAN_NOTES:
        folder_path = f'{root}_vault'
        write_obsidian_notes(folder_path, people)


if __name__ == "__main__":
    main(sys.argv[1], OBSIDIAN_NOTES)
