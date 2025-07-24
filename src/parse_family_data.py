#!/usr/bin/env python
import sys
import re

RECORD_MARKER = '$#K'
IMAGE_MARKER = '{bmc '
NO_DATE = 'o.D.'
LINK_MARKER = '>main'
image_pattern = re.compile(r'{bmc (.*?)\.BMP}')


class Person:
    name = None
    children = []
    father = None
    mother = None
    desc = None
    birth = None
    death = None
    documents = []
    spouses = []
    image = None


def add_person(people, person, key):
    if key:
        people[key] = person


def change_state(state, new_state, person, text):
    if state == 'name_required':
        if text:
            person.name = text.strip()
    if state == 'desc_awaited':
        if text:
            person.desc = text.strip()
    if state == 'father_awaited':
        if text:
            person.father = text.strip()
    if state == 'mother_awaited':
        if text:
            person.mother = text.strip()
    return new_state


def print_people(people):
    for personId in people:
        print(people[personId].name)
        print(people[personId].image)
        print(people[personId].desc)
        print(people[personId].father)
        print(people[personId].mother)


def main(file_path):
    with open(file_path, 'r', encoding='utf-8') as w:
        lines = w.read().split('\n')

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
            state = change_state(state, 'name_required', person, '')
        elif line.startswith(IMAGE_MARKER):
            image = image_pattern.search(line).group(1)
            if image:
                person.image = image
        elif state == 'name_required':
            if line:
                state = change_state(state, 'desc_awaited', person, line)
        else:
            text.append(line)
    add_person(people, person, key)
    print_people(people)


if __name__ == "__main__":
    main(sys.argv[1])
