#!/usr/bin/env python3

from sys import argv

import matplotlib.pyplot as plt

from movie import Movie
from crawler import Crawler
import general 

MOVIES_LIST_PATH = 'movies.txt'
BAR_CHART_PATH = 'number_of_movies_for_each_director.pdf'
ACTORS_GRAPH_PATH = 'actors_graph.pdf'
RATING_PATH = 'Rating/'


def read_movies_list_file(path):
    movies = []
    with open(path, 'r') as f:
        content = f.readlines()
    for item in content:
        movies.append(Movie.parse(item))
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
        director = movie.director
        if director in num_of_movies.keys():
            num_of_movies[director] += 1
        else:
            num_of_movies[director] = 1
    return num_of_movies

def readRatingsFromFiles():
    filenames = general.getFilenamesInFolder(RATING_PATH)
    file_content = []
    for name in filenames:
        content = general.readFile(name)
        file_content.append(content)
    return file_content

def main():
    if '--crawl' in argv:
        movies, actors_graph = Crawler(MOVIES_LIST_PATH).crawl_the_website()
        actors_graph.print_graph(ACTORS_GRAPH_PATH)
        draw_bar_chart(count_movies_by_a_director(movies), BAR_CHART_PATH)
    elif '--file' in argv:
        draw_bar_chart(count_movies_by_a_director(read_movies_list_file(MOVIES_LIST_PATH)), BAR_CHART_PATH)
        ratings = readRatingsFromFiles()
    else:
        print('''IMDB Crawler
flags:
    --crawl:    crawl the website
    --file:     use the file
        ''')


if __name__ == '__main__':
    main()
