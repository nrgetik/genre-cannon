#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
from pprint import pprint
import sys
import yaml

def dictify_nested_ul(ul):
    result = {}
    for li in ul.find_all('li', recursive=False):
        key = next(li.stripped_strings)
        ul = li.find('ul')
        if ul:
            result[key] = dictify_nested_ul(ul)
        else:
            result[key] = None
    return result

r = requests.get('https://en.wikipedia.org/wiki/List_of_popular_music_genres')
bowl = BeautifulSoup(r.text)
# just a starting point
cup = bowl.find('div', id='mw-content-text')

exclude = [
    'Contents',
    'Navigation Menu',
    'Exclusions',
    'References',
    'Bibliography'
]

genre_tree = {}

for span_tag in cup.find_all('span', class_='mw-headline'):
    # we don't care about wikipedia article housekeeping
    if any(exclusion in span_tag.string for exclusion in exclude):
        continue
    if span_tag.parent.name == 'h2':
        most_recent_h2 = span_tag.string
        level = 'primary'
    elif span_tag.parent.name == 'h3':
        level = 'secondary'
    # if the section has multiple columns, this will be one of two possible div tags,
    # otherwise it's the ul that we're actually looking for
    maybe_div_tag = span_tag.parent.next_sibling.next_sibling
    maybe_div_class_key = maybe_div_tag.get('class')
    # check on that and do necessary posturing-
    if maybe_div_class_key is not None and 'hatnote' in maybe_div_class_key:
        target_tag = maybe_div_tag.next_sibling.next_sibling
    else:
        target_tag = maybe_div_tag
    if 'div' in target_tag.name:
        target_tag = target_tag.find_next('ul')
    # build our tree
    if level == 'primary':
        genre_tree.setdefault(span_tag.string, dictify_nested_ul(target_tag))
    elif level == 'secondary':
        genre_tree.setdefault(most_recent_h2).setdefault(span_tag.string, dictify_nested_ul(target_tag))

pprint(genre_tree, width=1)

print(sys.getrecursionlimit())

# let's poop out some yaml
with open('genres-tree.yaml', 'w') as yaml_outfile:
    yaml_outfile.write(yaml.dump(genre_tree, default_flow_style=False))

# and a flattened version, just-in-case

