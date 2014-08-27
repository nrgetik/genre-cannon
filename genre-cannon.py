#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests

def find_some_child(tag):
    if tag.string is None:
        find_some_child(tag.child)
    else:
        return tag.child

r = requests.get('https://en.wikipedia.org/wiki/List_of_popular_music_genres')
soup = BeautifulSoup(r.text)

exclude = ['Contents', 'Navigation Menu', 'Exclusions', 'References', 'Bibliography']

genres = {}

for tag in soup.find_all('h2'):
    if tag.string is None:
        tag = tag.child
        #if (any(exclusion in tag.string for exclusion in exclude)):
        #    continue
        print tag.string
        for child in tag.children:
            if child.string is not None:
                #if any(exclusion in child.string for exclusion in exclude):
                #    continue
                print child.string
    #if tag.children is not None:
        #if any(exclusion in tag.string for exclusion in exclude):
        #    continue
    #    print tag.child.string
    #    print 'asdf'
    #if tag.parent.name == 'h2':
    #    genres[tag.string] = {}
    #    for tag2 in tag.find_all('span', class_='mw-headline'):
    #        if tag.parent.name == 'h2':
    #            print(tag.string)
    #if tag.parent.name == 'h3':
        #print(tag.string)
        #print(tag.parent.previous_sibling.previous_sibling['class'])
       # #genres[tag.name.previous_sibling.previous_sibling.child.string] = tag.string
