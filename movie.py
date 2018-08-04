#!/usr/bin/env python3

import copy


class Movie:
    def __init__(self):
        self.title = ''
        self.director = ''
        self.actors = []

    def set_title(self, title):
        self.title = title

    def set_director(self, director):
        self.director = director

    def set_all(self, title, director):
        self.title = title
        self.director = director

    def get_all_info(self):
        return self.title + '#' + self.director + '\n'

    def get_director(self):
        return self.director

    def get_title(self):
        return self.title

    def get_actors(self):
        return self.actors

    def set_actors(self, actors):
        self.actors = copy.deepcopy(actors)
