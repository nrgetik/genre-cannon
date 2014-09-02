#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
#from pprint import pprint

def find_dict_depth(node, depth=0):
    if not isinstance(node, dict) or not node:
        return depth
    return max(find_dict_depth(value, depth+1) for key, value in node.iteritems())

def walk_dict(node):
    for key, value in node.items():
        if isinstance(value, dict):
            if not value:
                print('find '+key)
            else:
                print('find  '+key)
                walk_dict(value)

r = requests.get('https://en.wikipedia.org/wiki/List_of_popular_music_genres')
bowl = BeautifulSoup(r.text)
cup = bowl.find('div', id='mw-content-text')

exclude = [
    'Contents',
    'Navigation Menu',
    'Exclusions',
    'References',
    'Bibliography'
]

top_level_genres = {}

for span_tag in cup.find_all('span', class_='mw-headline'):
    # we don't care about wikipedia article housekeeping
    if any(exclusion in span_tag.string for exclusion in exclude):
        continue
    if span_tag.parent.name == 'h2':
        top_level_genres.setdefault(span_tag.string, {})
        most_recent_h2 = span_tag.string
        level = 'primary'
    elif span_tag.parent.name == 'h3':
        top_level_genres.setdefault(most_recent_h2, {}).setdefault(span_tag.string, {})
        level = 'secondary'
    # if the section has multiple columns, this will be one of two possible div tags,
    # otherwise it's the ul that we're actually looking for
    maybe_div_tag = span_tag.parent.next_sibling.next_sibling
    maybe_div_class_key = maybe_div_tag.get('class')
    # check on that and do necessary cleanup-
    if maybe_div_class_key is not None and 'hatnote' in maybe_div_class_key:
        target_tag = maybe_div_tag.next_sibling.next_sibling
    else:
        target_tag = maybe_div_tag
    if 'div' in target_tag.name:
        target_tag = target_tag.find_next('ul')
    print(target_tag.name)
