#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import string
import requests


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


def count_genres_occ(node, occs):
    """Keep a count of number of children for each node.
    """
    for key, value in sorted(node.items()):
        key = key.encode('utf8').lower()
        if isinstance(value, dict):
            if key in occs.keys():
                occs[key].append(len(value.items()))
            else:
                occs[key] = [len(value.items())]
            count_genres_occ(value, occs)
        else:
            if key in occs.keys():
                occs[key].append(1)
            else:
                occs[key] = [1]

def is_best_occ(genre, occs):
    """When genre present multiple time, keep the location with most children
    """   
    try:
        num_childs = occs[genre].pop(0)
    except IndexError as e:
        print 'Skipping %s' % genre
        return False # better occurence has already been written

    if occs[genre] and num_childs < max(occs[genre]):
        # there are others occurences with more childs, skip this one
        print 'Skipping %s' % genre
        return False

    occs[genre] = []
    return True


def produce_yaml_from_dict(node, local_fh, occs, spacer='- '):
    """Write yaml from dict by excluding some keys to avoid duplicate genres.
    """
    for key, value in sorted(node.items()):
        key = key.encode('utf8').lower()
        if isinstance(value, dict):
            if is_best_occ(key, occs):
                local_fh.write('%s%s:\n' % (spacer, key))
            produce_yaml_from_dict(value, local_fh, occs, '    ' + spacer)
        else:
            if is_best_occ(key, occs):
                local_fh.write('%s%s\n' % (spacer, key))


def get_wikipedia_data():
    r = requests.get(
        'https://en.wikipedia.org/wiki/List_of_popular_music_genres')
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
            genre_tree.setdefault(
                span_tag.string,
                dictify_nested_ul(target_tag))
        elif level == 'secondary':
            genre_tree.setdefault(most_recent_h2).setdefault(
                span_tag.string,
                dictify_nested_ul(target_tag))

    return genre_tree


def check_genres_occ(fh):
    """Print a warning if genres appear multiple times in the output"""

    yaml = fh.readlines()
    done_genres = set()
    dup_genres = set()
    for line in yaml:
        genre = string.strip(string.strip(line), ":-")
        if genre not in done_genres:
            done_genres.add(genre)
        else:
            dup_genres.add(genre)
    if dup_genres:
        print "Warning: duplicated genres %s" % sorted(list(dup_genres))


if __name__ == '__main__':
    genre_tree = get_wikipedia_data()

    # let's poop out some yaml
    with open('genres-tree.yaml', 'w+') as fh:
        occs = {}
        count_genres_occ(genre_tree, occs)
        produce_yaml_from_dict(genre_tree, fh, occs)
        fh.seek(0)
        check_genres_occ(fh)
