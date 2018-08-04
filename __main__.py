#!/usr/bin/env python3

import copy
from sys import stderr

import requests
import matplotlib.pyplot as plt
import networkx as nx
from bs4 import BeautifulSoup


MAIN_URL = 'https://www.imdb.com/title/'
MOVIES_LIST_PATH = 'movies.txt'
BAR_CHART_PATH = 'number_of_movies_for_each_director.pdf'
ACTORS_GRAPH_PATH = 'actors_graph.pdf'

MAX_MOVIE_COUNT = 100
MAX_UNAVAILABLE_COUNT = 20


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


class ActorsGraph:
    def __init__(self):
        self.graph = nx.Graph()

    def add_edges(self, actors):
        if len(actors) <= 1:
            for actor in actors:
                if actor not in self.graph:
                    self.graph.add_node(actor)
            return
        for actor1 in actors:
            for actor2 in actors:
                if not(actor1 == actor2):
                    if actor1 not in self.graph:
                        self.graph.add_node(actor1)
                    if actor2 not in self.graph:
                        self.graph.add_node(actor2)
                    if self.is_connected(actor1, actor2):
                        self.graph[actor1][actor2]['weight'] += 1
                    else:
                        self.graph.add_edge(actor1, actor2, weight=1)

    def is_connected(self, u, v):
        return u in self.graph.neighbors(v)

    def print_graph(self, path):
        elarge = [(u, v) for (u, v, d) in self.graph.edges(data=True) if d['weight'] > 2]
        esmall = [(u, v) for (u, v, d) in self.graph.edges(data=True) if d['weight'] <= 2]

        pos = nx.spring_layout(self.graph)  # positions for all nodes

        # nodes
        nx.draw_networkx_nodes(self.graph, pos, node_size=400)

        # edges
        nx.draw_networkx_edges(self.graph, pos, edgelist=elarge, width=3)
        nx.draw_networkx_edges(self.graph, pos, edgelist=esmall, width=1, alpha=0.5, edge_color='b', style='dashed')
        labels = nx.get_edge_attributes(self.graph, 'weight')
        edge_labels = dict([((u, v), d['weight']) for u, v, d in self.graph.edges(data=True)])
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        # labels
        nx.draw_networkx_labels(self.graph, pos, font_size=8, font_family='sans-serif')

        plt.axis('off')
        plt.savefig(path)  # save as pdf
        plt.show()  # display


def get_page_content(url):
    r = requests.get(url)
    if not r.status_code == 200:
        raise RuntimeError('Problem accessing page data.')
    return r.text


def get_movie_name(content):
    soup = BeautifulSoup(content, 'html.parser')
    all_h1 = soup.find_all('h1')
    title = [x for x in all_h1 if 'itemprop="name"' in str(x)]
    title = str(title[0])
    title = title.split('>')
    title = title[1].split('<')[0]
    return title


def get_director_name(content):
    soup = BeautifulSoup(content, 'html.parser')
    all_spans = soup.find_all('span')
    director = [x for x in all_spans if 'itemprop="director"' in str(x)]
    if len(director) == 0:
        return ''
    director = str(director[0]).split('>')[-4]
    director = director.split('<')[0]
    return director


def change_movie_url(count, prefix):
    if count < 10:
        return prefix + '000000' + str(count)
    if count >= 10 and count < 100:
        return prefix + '00000' + str(count)
    if count >= 100 and count < 1000:
        return prefix + '0000' + str(count)
    if count >= 1000 and count < 10000:
        return prefix + '000' + str(count)
    if count >= 10000 and count < 100000:
        return prefix + '00' + str(count)
    if count >= 100000 and count < 1000000:
        return prefix + '0' + str(count)
    if count >= 1000000 and count < 10000000:
        return prefix + str(count)


def write_results_to_file(item):
    thefile = open(MOVIES_LIST_PATH, 'a')
    thefile.write(item)
    thefile.close()


def get_movie_actors(content):
    soup = BeautifulSoup(content, 'html.parser')
    all_tds = soup.find_all('td')
    cast_tds = [x for x in all_tds if 'itemprop="actor"' in str(x)]
    cast_span = [x.find_all('span') for x in cast_tds]
    cast_names = []
    for item in cast_span:
        for nestedItem in item:
            cast_names.append(nestedItem.text)
    return cast_names


def crawl_the_website():
    movies = []
    count = 0
    actors_graph = ActorsGraph()
    count_not_found = 0
    while count < MAX_MOVIE_COUNT and count_not_found < MAX_UNAVAILABLE_COUNT:
        count += 1
        print('Crawling...' + str(count), file=stderr)
        this_movie_url = change_movie_url(count, 'tt')
        try:
            content = get_page_content(MAIN_URL + this_movie_url + '/')
            count_not_found = 0
            title = get_movie_name(content)
            director = get_director_name(content)
            actors = get_movie_actors(content)
            actors_graph.add_edges(actors)
            this_movie = Movie()
            this_movie.set_all(title, director)
            this_movie.set_actors(actors)
            movies.append(this_movie)
            write_results_to_file(movies[-1].get_all_info())
        except RuntimeError:
            print('Movie not found.', file=stderr)
            count_not_found += 1
    return movies, actors_graph


def read_movies_list_file(path):
    movies = []
    thefile = open(path, 'r')
    content = thefile.readlines()
    thefile.close()
    for item in content:
        x = item.strip()
        x = x.split('#')
        y = Movie()
        y.set_all(x[0], x[-1])
        movies.append(y)
    return movies


def draw_bar_chart(num_of_movies, path):
    x = []
    y = []
    for item in num_of_movies.keys():
        if item == '':
            continue
        x.append(item)
        y.append(num_of_movies[item])
    plt.bar(x, y)
    plt.savefig(path)
    plt.show()


def count_movies_by_a_director(movies):
    num_of_movies = {}
    for movie in movies:
        director = movie.get_director()
        if director in num_of_movies.keys():
            num_of_movies[director] += 1
        else:
            num_of_movies[director] = 1
    return num_of_movies


if __name__ == '__main__':
    choice = input('1. crawl the website 2. use the file (1/2) ')
    if choice == '1':
        movies, actors_graph = crawl_the_website()
        actors_graph.print_graph(ACTORS_GRAPH_PATH)
    elif choice == '2':
        movies = read_movies_list_file(MOVIES_LIST_PATH)
    draw_bar_chart(count_movies_by_a_director(movies), BAR_CHART_PATH)
