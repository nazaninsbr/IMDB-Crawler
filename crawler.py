from sys import stderr
from math import log10
import os 

import requests
from bs4 import BeautifulSoup

from actors_graph import ActorsGraph
from movie import Movie

DEFAULT_MAX_MOVIE_COUNT = 10010
DEFAULT_MAX_UNAVAILABLE_COUNT = 20
DEFAULT_RATING_FOLDER = 'Rating/'


class Crawler(object):
	main_url = 'https://www.imdb.com/title/'
	rating_url_ending = 'ratings?ref_=tt_ov_rt'
	
	def __init__(self, movies_list_path,
				 max_movie_count=DEFAULT_MAX_MOVIE_COUNT,
				 max_unavailable_count=DEFAULT_MAX_UNAVAILABLE_COUNT, 
				 rating_folder =DEFAULT_RATING_FOLDER):
		self.movies_list_path = movies_list_path
		self.max_movie_count = max_movie_count
		self.max_unavailable_count = max_unavailable_count
		self.rating_folder = rating_folder
		self.create_project_dir(self.rating_folder)

		self.max_diff_movie = ''
		self.max_diff = 0

	def create_project_dir(self, directory):
		if not os.path.exists(directory):
			print('Creating Project Folder'+ directory)
			os.makedirs(directory)

	def get_page_content(self, url):
		r = requests.get(url)
		if not r.status_code == 200:
			raise RuntimeError('Problem accessing page data.')
		return r.text

	def get_movie_name(self, content):
		soup = BeautifulSoup(content, 'html.parser')
		all_h1 = soup.find_all('h1')
		title = [x for x in all_h1 if 'itemprop="name"' in str(x)]
		if len(title)==0:
			title = [x for x in all_h1 if 'id="titleYear"' in str(x)]
		title = str(title[0]).split('>')[1].split('<')[0]
		print('Title: '+title)
		return title

	def get_director_name(self, content):
		soup = BeautifulSoup(content, 'html.parser')
		all_spans = soup.find_all('span')
		director = [x for x in all_spans if 'itemprop="director"' in str(x)]
		if len(director) == 0:
			all_as = soup.find_all('a')
			director = [x for x in all_as if ('href="/name/nm' in str(x))]
			# print('director:' + director[2].text)
			director = director[2].text
		else:
			director = str(director[0]).split('>')[-4].split('<')[0]
		return director

	def change_movie_url(self, number, prefix):
		return prefix + max([6 - int(log10(number)), 0]) * '0' + str(number)

	def write_results_to_file(self, item):
		with open(self.movies_list_path, 'a') as f:
			f.write(str(item))

	def write_rating_results_to_file(self, item):
		filename = item.title+'.txt'
		with open(self.rating_folder+filename, 'a') as f:
			f.write(item.get_rating())

	def get_movie_actors(self, content):
		soup = BeautifulSoup(content, 'html.parser')
		all_tds = soup.find_all('td')
		cast_tds = [x for x in all_tds if 'itemprop="actor"' in str(x)]
		if len(cast_tds)==0:
			cast_names = []
			tables = soup.find_all('table')
			cast_table = [x for x in tables if 'class="cast_list"' in str(x)]
			if len(cast_table)==0:
				return []
			all_trs = cast_table[0].find_all('tr')
			for tr in all_trs[1:]:
				all_tds = tr.find_all('td')
				if len(all_tds)<2:
					continue
				all_as = all_tds[1].find_all('a')
				name = all_as[0].text
				name = name.replace(' ', '')
				name = name.replace('\n', '')
				cast_names.append(name)
		else:
			cast_span = [x.find_all('span') for x in cast_tds]
			cast_names = []
			for item in cast_span:
				for nestedItem in item:
					cast_names.append(nestedItem.text)
		return cast_names

	def get_rating_percentages(self, table_content):
		result = []
		all_tds = table_content.find_all('td')
		count = 0
		for td in all_tds:
			count +=1
			divs = td.find_all('div')
			if len(divs)>=2:
				percentage = divs[1].text
			else:
				percentage = '-'
			if count%3==2:
				percentage = percentage.replace(' ', '')
				percentage = percentage.replace('\n', '')
				percentage = percentage.replace('\xa0', '')
				percentage = percentage.replace('%', '')
				result.append(percentage)
		return result

	def get_rating_by_demographic(self, table_content):
		# [[all], [males], [females]]
		# all , <18, 18-29, 30-44, 45+
		result = []
		all_trs = table_content.find_all('tr')
		for tr in all_trs[1:]:
			result.append([])
			all_tds = tr.find_all('td')
			for td in all_tds[1:]:
				divs = td.find_all('div')
				rating = divs[0].text
				result[-1].append(rating)
		return result[0][0], result

	def get_us_non_us_rating(self, table_content):
		result = []
		vote_count = []
		all_tds = table_content.find_all('td')
		for td in all_tds:
			divs = td.find_all('div')
			if len(divs)>=2:
				count = divs[1].text
				count = count.replace(' ', '')
				count = count.replace('\n', '')
			else:
				count = '-'
			vote_count.append(count)
			result.append(divs[0].text)
		return result[1], vote_count[1], result[2], vote_count[2]

	def get_rating_information(self, content):
		soup = BeautifulSoup(content, 'html.parser')
		all_tables = soup.find_all('table')
		rating_percentages = self.get_rating_percentages(all_tables[0])
		general_rating, rating_by_demographic = self.get_rating_by_demographic(all_tables[1])
		us_rating, us_votes, non_us_rating, non_us_votes= self.get_us_non_us_rating(all_tables[2])
		result = {'rating': general_rating, 'percentages': rating_percentages, 'demographic': rating_by_demographic, 'us': us_rating, 'non-us':non_us_rating}
		if us_votes>'300' and non_us_votes>'300' and not us_rating=='-' and not non_us_rating=='-':
			return result, 1
		return result, 0

	def all_rating_information(self, number):
		url = self.main_url+'tt'+max([6 - int(log10(number)), 0]) * '0'+str(number)+'/'+self.rating_url_ending
		content = self.get_page_content(url)
		if 'No Ratings Available' in str(content) or content==-1:
			return {'rating': '-', 'percentages': '-', 'demographic': ['-', '-', '-'], 'us': '-', 'non-us':'-'}, 0
		return self.get_rating_information(content)


	def get_movie_language(self, content):
		soup = BeautifulSoup(content, 'html.parser')
		all_as = soup.find_all('a')
		lang_as = [x for x in all_as if('href="/search/title?title_type=feature&primary_language="' in str(x) and "&sort=moviemeter,asc&ref_=tt_dt_dt" in str(x))]
		if len(lang_as)==0:
			return ''
		else:
			print(lang_as)
			print(lang_as[0].text)
			return lang_as[0].text	
			exit()


	def check_if_max_diff(self, us, non_us, title):
		if abs(float(us)-float(non_us))>self.max_diff:
			self.max_diff = abs(float(us)-float(non_us))
			self.max_diff_movie = title

	def crawl_the_website(self):
		movies = []
		count = 10000
		actors_graph = ActorsGraph()
		count_not_found = 0
		while count < self.max_movie_count and count_not_found < self.max_unavailable_count:
			count += 1
			this_movie_url = self.change_movie_url(count, 'tt')
			print('Crawling... ' + str(count) + ' ... ' + this_movie_url, file=stderr)
			try:
				content = self.get_page_content(self.main_url + this_movie_url + '/')
				count_not_found = 0
				title = self.get_movie_name(content)
				# language = self.get_movie_language(content)
				director = self.get_director_name(content)
				actors = self.get_movie_actors(content)
				rating_information, consider_for_max_diff = self.all_rating_information(count)
				if consider_for_max_diff==1:
					self.check_if_max_diff(rating_information['us'], rating_information['non-us'], title)
				actors_graph.add_edges(actors)
				movies.append(Movie(title, director, language, actors, rating_information))
				self.write_results_to_file(movies[-1])
				self.write_rating_results_to_file(movies[-1])
			except RuntimeError as e:
				print(e, file=stderr)
				count_not_found += 1
		print('Movie with max us, non-us diff is: '+ self.max_diff_movie)
		return movies, actors_graph
