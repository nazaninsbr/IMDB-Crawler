#!/usr/bin/env python3

import matplotlib.pyplot as plt

from movie import Movie
from crawler import Crawler

MOVIES_LIST_PATH = 'movies.txt'
BAR_CHART_PATH = 'number_of_movies_for_each_director.pdf'
ACTORS_GRAPH_PATH = 'actors_graph.pdf'


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
        movies, actors_graph = Crawler(MOVIES_LIST_PATH).crawl_the_website()
        actors_graph.print_graph(ACTORS_GRAPH_PATH)
    elif choice == '2':
        movies = read_movies_list_file(MOVIES_LIST_PATH)
    draw_bar_chart(count_movies_by_a_director(movies), BAR_CHART_PATH)
