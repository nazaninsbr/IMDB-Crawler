#!/usr/bin/env python3

import copy
from rating import Rating 

class Movie:
    def __init__(self, title='', director='', actors=[], rating_information={}):
        self.title = title
        self.director = director
        self.actors = actors
        self.rating = Rating(rating_information)

    def __str__(self):
        return self.title + '#' + self.director + '\n'

    @property
    def actors(self):
        return self._actors

    @actors.setter
    def actors(self, actors):
        self._actors = copy.deepcopy(actors)

    @classmethod
    def parse(cls, string):
        parsed = string.strip().split('#')
        return Movie(parsed[0], parsed[1])

    def get_rating(self):
        return str(self.rating)

    

    
    
