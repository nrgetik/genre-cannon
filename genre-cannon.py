#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
from pprint import pprint

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
    if any(exclusion in span_tag.string for exclusion in exclude):
        continue
    if span_tag.parent.name == 'h2':
        top_level_genres.setdefault(span_tag.string, {})
        most_recent_h2 = span_tag.string
    elif span_tag.parent.name == 'h3':
        top_level_genres.setdefault(most_recent_h2, {}).setdefault(span_tag.string, {})

pprint(top_level_genres, width=1)
